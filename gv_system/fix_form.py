import re

filepath = r'c:\Users\Admin\Desktop\backup\GBV_SYSTEM\gv_system\reports\templates\reports\file_report.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Check current state
idx = content.find('value="Doxing"')
if idx >= 0:
    print('Found old Doxing option - replacing...')
    # Find the select block for incident_category and replace options
    # Pattern to find the select content
    old_select_start = 'value="">Select Type of abuse</option>'
    old_select_end = 'value="Sextortion">Sextortion</option>'
    
    start_idx = content.find(old_select_start)
    end_idx = content.find(old_select_end)
    
    if start_idx >= 0 and end_idx >= 0:
        end_idx = end_idx + len(old_select_end)
        new_options = """value="">Select Type of abuse</option>
                                    <option value="cyberstalking">Cyberstalking &amp; Harassment</option>
                                    <option value="doxing">Non-Consensual Image Sharing / Doxing</option>
                                    <option value="impersonation">Impersonation &amp; Identity Theft</option>
                                    <option value="threats">Online Threats &amp; Hate Speech</option>
                                    <option value="other">Other Forms of Online Abuse</option>
                                    <option value="children_home_support">Children's Home Support</option"""
        content = content[:start_idx] + new_options + content[end_idx:]
        print('Category options replaced successfully')
    else:
        print(f'Could not find selection bounds: start={start_idx}, end={end_idx}')
else:
    print('Old Doxing option not found - checking if already fixed')
    if 'value="cyberstalking"' in content:
        print('Already using correct cyberstalking value')
    else:
        print('Unknown state - checking content around incident_category')
        idx2 = content.find('id_incident_category')
        print(repr(content[idx2:idx2+500]))

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - file saved')
