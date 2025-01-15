import urllib.parse

# Step 1: Provide the direct download URL of your PPTX file on Google Drive
pptx_url = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"

# Step 2: URL-encode the PPTX file URL for embedding
encoded_url = urllib.parse.quote(pptx_url, safe='')

# Step 3: Construct the Office Online embed URL using the encoded URL
embed_url = f"https://view.officeapps.live.com/op/embed.aspx?src={encoded_url}"

# Step 4: Create the HTML content with an iframe embedding the PPTX presentation
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Embedded PPTX Presentation</title>
</head>
<body>
  <iframe 
    src="{embed_url}" 
    width="100%" 
    height="600px" 
    frameborder="0">
  </iframe>
</body>
</html>
"""

# Step 5: Write the HTML content to a file
with open("embedded_pptx.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML file 'embedded_pptx.html' has been created.")
