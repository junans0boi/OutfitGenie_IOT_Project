#C:\WebServer\HollyWood\OutfitGenie\Gemini\OutfitGenie_LLM.py
SYSTEM_TEMPLATE = """###참고자료###

{context}

###질문###
"""

HUMAN_TEMPLATE = "{question}"

import sys
PDF_LIST = [f"{sys.path[0]}/Outfit Coordination Guide.pdf"]