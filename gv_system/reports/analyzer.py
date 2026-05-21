def analyze_incident_text(description_text):
    """
    Scans the report text for specific threat risk factors.
    Returns calculated risk score, priority level, and an array of detected tags.
    """
    text = description_text.lower()
    
    # Weight arrays for priority flagging
    critical_keywords = ['kill', 'suicide', 'die', 'murder', 'physical harm', 'stab', 'find you', 'where you live', 'track you']
    high_keywords = ['leak', 'naked', 'photo', 'video', 'nude', 'post online', 'expose', 'blackmail', 'extort', 'money', 'dox']
    medium_keywords = ['fake profile', 'impersonating', 'calling me', 'messages', 'insult', 'harassing', 'stalking']
    
    risk_score = 0
    detected_tags = []
    
    # Check for Critical Threats
    for word in critical_keywords:
        if word in text:
            risk_score += 4
            if "Physical Threat" not in detected_tags:
                detected_tags.append("Physical Threat")
                
    # Check for High Threats (Image-based abuse/Extortion)
    for word in high_keywords:
        if word in text:
            risk_score += 3
            if "Privacy Compromise" not in detected_tags:
                detected_tags.append("Privacy Compromise")
                
    # Check for Medium Threats (General Harassment)
    for word in medium_keywords:
        if word in text:
            risk_score += 1
            if "Harassment Vector" not in detected_tags:
                detected_tags.append("Harassment Vector")

    # Enforce a ceiling limit of 10 for the score metrics
    if risk_score > 10:
        risk_score = 10
        
    # Translate final score array to an administrative triage priority tier
    if risk_score >= 7:
        priority_level = 'critical'
    elif risk_score >= 5:
        priority_level = 'high'
    elif risk_score >= 2:
        priority_level = 'medium'
    else:
        priority_level = 'low'
        
    return risk_score, priority_level, ", ".join(detected_tags)