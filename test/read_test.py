import json

import unittest

from langgraph.graph.graph import CompiledGraph

from tools import summarize, extract_from_manual, extract_organization_level_data
from tools.query_rewrite import multi_query_rewrite
from utils.llm_configuration import GoogleLLMConfiguration as Configuration
from pydantic import BaseModel

from workflow import Workflow

configuration = Configuration()
llm = configuration.get_llm()

class Output(BaseModel):
    name: str
    manufacturer: str
    model_number: str
    characteristics: list[str]

class Test(unittest.TestCase):
    def test_scenario_1(self):
        workflow = multi_query_rewrite(
            {"query": "Give me all the list of equipments and it's 2 unique characteristics for Maritime"})
        print(workflow)
        for step in workflow["steps"]:
            print(step.order)
            print(step.tool)
            print(step.reason_it_was_chosen)
        self.assertEquals(workflow["steps"][0].tool, "extract_organization_level_data")
        self.assertEquals(workflow["steps"][1].tool, "extract_from_manual")
        self.assertEquals(workflow["steps"][2].tool, "summarize")

    def test_scenario_2(self):
        workflow = multi_query_rewrite({"query": "What is the weight of CAT-032?"})
        print(workflow)
        for step in workflow["steps"]:
            print(step.order)
            print(step.tool)
            print(step.reason_it_was_chosen)
        self.assertEquals(workflow["steps"][0].tool, "extract_from_manual")
        self.assertEquals(workflow["steps"][1].tool, "summarize")

    def test_scenario_3(self):
        workflow = multi_query_rewrite({"query": "Tell me a story of a camel and it's owner."})
        print(workflow)
        for step in workflow["steps"]:
            print(step.order)
            print(step.tool)
            print(step.reason_it_was_chosen)
        self.assertEquals(workflow["steps"][0].tool, "summarize")

    def test_workflow(self):
        workflow: CompiledGraph = Workflow().create_graph()
        for c in workflow.invoke({"query": "Give me all the list of equipments and then from the user manual give me 2 characteristics for Maritime"}):
            print(c)

    def test_scenario_10(self):
        equips_str = extract_organization_level_data("""
                                        Give me list of equipments in the Maritime as a json array of strings.
                                        Always return a valid json response do not send back any extra texts.
    
                                        Example:
                                        Question:
                                            give me the list of fruits starting with letter 'a'.
                                        Answer:
                                            ["apple", "apricot", "apple lemon"]
                                      """).content
        equips:list[str] = json.loads(equips_str)
        assert len(equips) == 6

        for equip in equips:
            equip_struct_llm = configuration.get_llm().with_structured_output(Output)
            query = f"""
                            Need you to return me the name, model number, manufacturer and characteristics details this equipment: {equip}.
                            Expected format is similar to following.
                            {{
                                "name": "laptop",
                                "model_number": "MacBookPro",
                                "manufacturer":"apple",
                                "characteristics": ["service every 6 months, so that apple can make a lot of money."]
                            }}
                            
                            Note: These are some of the manufacturers that I know of. 
                                  If the name is kind of from following list use the name from the list instead. 
                                - 'Wärtsilä'
                                - 'Caterpillar'
                                - 'Alfa Laval'
                                - 'MAN B&W'
                                - 'Framo'
                            
                    """
            manual = extract_from_manual(query)
            summary = summarize(manual)
            output: Output = equip_struct_llm.invoke(summary)
            self.assertIn(
                output.manufacturer, [
                    "Wärtsilä",
                    "Caterpillar",
                    "Alfa Laval",
                    "MAN B&W",
                    "Framo"
                ]
            )

if __name__ == '__main__':
    unittest.main()