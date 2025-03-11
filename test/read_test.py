import json

import unittest

from read import extract_organization_level_data, extract_from_manual, summarize, multi_query_rewrite
from tools.llm_configuration import GoogleLLMConfiguration as Configuration
from pydantic import BaseModel

configuration = Configuration()
llm = configuration.get_llm()

class Output(BaseModel):
    name: str
    manufacturer: str
    model_number: str
    characteristics: list[str]

class Test(unittest.TestCase):
    def test_scenario_1(self):
        workflow = multi_query_rewrite("Give me all the list of equipments and it's 2 unique characteristics for Maritime")
        print(workflow)
        for step in workflow.steps:
            print(step.order)
            print(step.tool)
            print(step.reason)
        self.assertEquals(workflow.steps[0].tool, "extract_organization_level_data")
        self.assertEquals(workflow.steps[1].tool, "extract_from_manual")
        self.assertEquals(workflow.steps[2].tool, "summarize")

    def test_scenario_2(self):
        workflow = multi_query_rewrite("What is the weight of CAT-032?")
        print(workflow.query)
        for step in workflow.steps:
            print(step.order)
            print(step.tool)
            print(step.reason)
        self.assertEquals(workflow.steps[0].tool, "extract_from_manual")
        self.assertEquals(workflow.steps[1].tool, "summarize")

    def test_scenario_3(self):
        workflow = multi_query_rewrite("Tell me a story of a camel and it's owner.")
        print(workflow.query)
        for step in workflow.steps:
            print(step.order)
            print(step.tool)
            print(step.reason)
            self.assertNotIn(step.tool, ['extract_organization_level_data', 'extract_from_manual'])


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
                                  If the name starts with one from this list use the following name instead. 
                                - 'Wärtsilä'
                                - 'Caterpillar'
                                - 'Alfa Laval'
                                - 'MAN B&W'
                                - 'Framo'
                            
                    """
            summary = summarize(extract_from_manual(query))
            output: Output = equip_struct_llm.invoke(summary)
            print(f"{equip}:\n", output)
            self.assertIn(
                output.manufacturer, [
                    "Wärtsilä",
                    "Caterpillar",
                    "Alfa Laval",
                    "MAN B&W",
                    "Framo"
                ]
            )