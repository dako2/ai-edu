import requests

"""
curl -i -X POST 'https://open.feishu.cn/open-apis/drive/v1/metas/batch_query?user_id_type=user_id' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer u-fntdD58ux2P8En52GG9UKahlhANklkT1h80040cy0dGD' \
-d '{
	"request_docs": [
		{
			"doc_token": "Uc3qsFE2DlK2TxdnSOvc9UXon0d",
			"doc_type": "doc"
		}
	],
	"with_url": false
}'
"""

class FeishuSlideService:
    def __init__(self, access_token="t-g104189n7MKTUHCRT7CEPWRYXWNRXQBSN2LJOCF6", presentation_id="Uc3qsFE2DlK2TxdnSOvc9UXon0d"):
        """
        Initialize the FeishuSlideService with access token and presentation ID.
        """
        self.access_token = access_token
        self.presentation_id = presentation_id
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def get_slides(self):
        """
        Fetch all slides in the presentation, including speaker notes.
        """
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{self.presentation_id}/slides"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        slides = response.json().get("data", {}).get("slides", [])
        slide_data = []
        for idx, slide in enumerate(slides):
            speaker_notes = self._get_speaker_notes(slide)
            slide_data.append({
                "slide_index": idx,
                "elements": slide.get("elements", []),
                "speaker_notes": speaker_notes,
            })
        return slide_data

    def _get_speaker_notes(self, slide):
        """
        Extract speaker notes from a slide.
        """
        notes = slide.get("speaker_notes", "")
        return notes

    def total_slides(self):
        """
        Return the total number of slides in the presentation.
        """
        slides = self.get_slides()
        return len(slides)

    def get_speaker_notes(self, slide_index):
        """
        Retrieve the speaker notes for a specific slide.
        """
        slides = self.get_slides()
        if 0 <= slide_index < len(slides):
            return slides[slide_index]["speaker_notes"]
        else:
            return {"error": "Invalid slide index."}

    def add_slide(self, layout="TITLE_AND_BODY", speaker_notes=""):
        """
        Add a new slide with optional speaker notes.
        """
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{self.presentation_id}/slides"
        data = {
            "layout": layout,
            "speaker_notes": speaker_notes,
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def update_speaker_notes(self, slide_id, notes):
        """
        Update speaker notes for a specific slide.
        """
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{self.presentation_id}/slides/{slide_id}/notes"
        data = {
            "notes": notes,
        }
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def show_slide(self, slide_index):
        """
        Generate a URL to display the specified slide.
        """
        slides = self.get_slides()
        if 0 <= slide_index < len(slides):
            slide_id = slides[slide_index]["slide_id"]
            url = f"https://open.feishu.cn/app/sheet/{self.presentation_id}?slide_id={slide_id}"
            return url
        else:
            return {"error": "Invalid slide index."}

slide = FeishuSlideService()
slide.total_slides()