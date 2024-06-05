SYSTEM_TEMPLATE = """###참고자료###

{context}

###문답예시###
"""

EXAMPLES = [
    {
        "question": "",
        "answer": ""
    },
    {
        "question": "",
        "answer": ""
    }
]

HUMAN_TEMPLATE = "질문: {question}\n답변: "

import sys
PDF_LIST = [f"{sys.path[0]}/IoT 텀프로젝트 제안서 Moodify.pdf"]