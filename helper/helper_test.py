# import json
# from typing import List
# from models import History
#
#
# def test_supervisor_and_general_manager(agent_class, ideal_answer: str, history: List[History], query: str):
#     response = agent_class.supervisor_and_general_manager(query, history)
#     try:
#         response_dict = json.loads(response)
#         type_, response_ = response_dict["type"], response_dict["response"]
#     except:
#         raise AssertionError("The response is not in JSON/Proper JSON format")
#     print("In Supervisor and General Manager, the response is: ", response)
#     score = agent_class.testing__evaluation_judge(response, ideal_answer)
#     return score
