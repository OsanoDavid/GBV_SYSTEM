from django.core.mail import send_mail
from django.conf import settings
from math import asin, cos, radians, sin, sqrt
import os
import requests

from reports.models import ChildrensHome, Department, IncidentReport, AuditLog


def distance_km(lat1, lng1, lat2, lng2):
    radius_km = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    )
    return 2 * radius_km * asin(sqrt(a))


class AssignmentService:
    OVERPASS_URL = os.getenv("OVERPASS_API_URL", "https://overpass-api.de/api/interpreter")
    SEARCH_RADII_METERS = (50000, 150000, 300000)

    @staticmethod
    def auto_route_report(report_id, user=None, user_lat=None, user_lng=None, nearest_home_id=None):
        """
        Inspects the report description, routes it to the correct department,
        and triggers an automated email notification.
        """
        report = IncidentReport.objects.get(pk=report_id)
        description = report.description.lower()
        
        nearest_home = None
        if report.incident_category == 'children_home_support':
            dept_name = "Children's Officer"
            dept_email = 'child_protection@safespace.org'
            nearest_home = AssignmentService.find_nearest_home(user_lat, user_lng, nearest_home_id)
        elif any(word in description for word in ['theft', 'steal', 'stolen', 'fraud']):
            dept_name = 'Police'
            dept_email = 'police@safespace.org'
        elif any(word in description for word in ['child', 'minor', 'kid', 'abuse']):
            dept_name = "Children's Officer"
            dept_email = 'child_protection@safespace.org'
        else:
            dept_name = 'General Support'
            dept_email = 'support@safespace.org'
            
        # Assign the department safely
        department, created = Department.objects.get_or_create(
            name=dept_name,
            defaults={'email': dept_email}
        )
        
        report.assigned_department = department
        if nearest_home:
            report.assigned_home = nearest_home
        if report.status == 'pending':
            report.status = 'under_review'
        report.save()
        
        # Trigger Email Notification
        try:
            send_mail(
                subject=f"New Incident Assigned: {report.reference_number}",
                message=(
                    f"A new incident has been routed to your department.\n\n"
                    f"Reference: {report.reference_number}\n"
                    f"Category: {report.incident_category}\n"
                    f"Details: {report.description[:200]}..."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[department.email],
                fail_silently=False,
            )
            email_status = "Email notification sent."
        except Exception as e:
            email_status = f"Email failed: {str(e)}"
        
        # Log this action for institutional transparency
        home_status = f" Nearest home assigned: {nearest_home.name}." if nearest_home else ""
        AuditLog.objects.create(
            report=report, 
            user=user, 
            action=f"Auto-routed to {dept_name} and marked under review.{home_status} {email_status}"
        )
        return department

    @staticmethod
    def find_nearest_home(user_lat, user_lng, nearest_home_id=None):
        if nearest_home_id:
            home = ChildrensHome.objects.filter(id=nearest_home_id).first()
            if home:
                return home

        try:
            lat = float(user_lat)
            lng = float(user_lng)
        except (TypeError, ValueError):
            return None

        AssignmentService.import_online_childrens_homes(lat, lng)

        nearest_home = None
        nearest_distance = None
        for home in ChildrensHome.objects.all():
            current_distance = distance_km(lat, lng, float(home.lat), float(home.lng))
            if nearest_distance is None or current_distance < nearest_distance:
                nearest_distance = current_distance
                nearest_home = home
        return nearest_home

    @staticmethod
    def get_nearby_homes(user_lat, user_lng, limit=5):
        try:
            lat = float(user_lat)
            lng = float(user_lng)
        except (TypeError, ValueError):
            return []

        AssignmentService.import_online_childrens_homes(lat, lng)

        homes = []
        for home in ChildrensHome.objects.all():
            home.distance = round(distance_km(lat, lng, float(home.lat), float(home.lng)), 2)
            homes.append(home)

        homes.sort(key=lambda home: home.distance)
        return homes[:limit]

    @staticmethod
    def import_online_childrens_homes(user_lat, user_lng):
        if AssignmentService.has_local_home_nearby(
            user_lat,
            user_lng,
            max(AssignmentService.SEARCH_RADII_METERS) / 1000,
        ):
            return 0

        imported_count = 0
        for radius in AssignmentService.SEARCH_RADII_METERS:
            results = AssignmentService.fetch_overpass_childrens_homes(user_lat, user_lng, radius)
            for result in results:
                if AssignmentService.save_online_home(result):
                    imported_count += 1
            if imported_count:
                break
        return imported_count

    @staticmethod
    def has_local_home_nearby(user_lat, user_lng, max_distance_km):
        for home in ChildrensHome.objects.all():
            current_distance = distance_km(user_lat, user_lng, float(home.lat), float(home.lng))
            if current_distance <= max_distance_km:
                return True
        return False

    @staticmethod
    def fetch_overpass_childrens_homes(user_lat, user_lng, radius):
        query = f"""
        [out:json][timeout:25];
        (
          node(around:{radius},{user_lat},{user_lng})["amenity"="social_facility"]["social_facility:for"~"child|orphan|juvenile",i];
          way(around:{radius},{user_lat},{user_lng})["amenity"="social_facility"]["social_facility:for"~"child|orphan|juvenile",i];
          relation(around:{radius},{user_lat},{user_lng})["amenity"="social_facility"]["social_facility:for"~"child|orphan|juvenile",i];
          node(around:{radius},{user_lat},{user_lng})["social_facility"~"group_home|orphanage",i]["name"~"child|children|orphan|orphanage|home",i];
          way(around:{radius},{user_lat},{user_lng})["social_facility"~"group_home|orphanage",i]["name"~"child|children|orphan|orphanage|home",i];
          relation(around:{radius},{user_lat},{user_lng})["social_facility"~"group_home|orphanage",i]["name"~"child|children|orphan|orphanage|home",i];
        );
        out center tags 25;
        """

        try:
            response = requests.post(
                AssignmentService.OVERPASS_URL,
                data={"data": query},
                headers={"User-Agent": "SafeSpace/1.0 children-home lookup"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("elements", [])
        except (requests.RequestException, ValueError):
            return []

    @staticmethod
    def save_online_home(element):
        tags = element.get("tags", {})
        name = (tags.get("name") or tags.get("operator") or "").strip()
        if not name:
            return None

        lat = element.get("lat") or element.get("center", {}).get("lat")
        lng = element.get("lon") or element.get("center", {}).get("lon")
        if lat is None or lng is None:
            return None

        lat = round(float(lat), 6)
        lng = round(float(lng), 6)
        existing = ChildrensHome.objects.filter(
            name__iexact=name,
            lat__gte=lat - 0.00001,
            lat__lte=lat + 0.00001,
            lng__gte=lng - 0.00001,
            lng__lte=lng + 0.00001,
        ).first()
        if existing:
            return existing

        address = AssignmentService.format_osm_address(tags)
        phone = (
            tags.get("phone")
            or tags.get("contact:phone")
            or tags.get("mobile")
            or "Not listed"
        )

        return ChildrensHome.objects.create(
            name=name[:200],
            phone=phone[:20],
            address=address,
            lat=lat,
            lng=lng,
        )

    @staticmethod
    def format_osm_address(tags):
        if tags.get("addr:full"):
            return tags["addr:full"]

        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb"),
            tags.get("addr:city"),
            tags.get("addr:county"),
            tags.get("addr:country"),
        ]
        address = ", ".join(part for part in address_parts if part)
        return address or "Address not listed"
