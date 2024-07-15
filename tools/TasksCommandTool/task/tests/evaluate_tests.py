from ..Task import Task, InterpretedTask
from .utils import TaskTest, test_info_a, test_pipeline_a, test_match_template_a, test_pipeline_b


class EvaluateTest(TaskTest):

    def assertInterpretEqual(self, actual: InterpretedTask, expected: dict):
        actual = actual.to_task_dict()
        for key in expected:
            if isinstance(actual[key], list):
                for i, value in enumerate(actual[key]):
                    if isinstance(value, Task):
                        value = value.name
                    self.assertEqual(value, expected[key][i], f"Key: {key}")
            else:
                self.assertEqual(expected[key], actual[key], f"Key: {key}")

    def test_evaluate(self):
        Task("A", {**test_info_a, **test_pipeline_a})
        Task("B", {**test_info_a, **test_pipeline_b})
        print(Task.evaluate("C@B@A"))

    def define_tasks(self):
        Task("A", {"next": ["N1", "N2"]})
        Task("C", {"next": ["B@A#next"]})
        Task("Loading", {"next": ["#self", "#next", "#back"]})
        Task("B", {"next": ["Other", "B@Loading"]})

    def test_2(self):
        self.define_tasks()
        self.assertInterpretEqual(Task.get("C").interpret(), {
            "name": "C",
            "next": ["B@N1", "B@N2"],
        })

    def test_3(self):
        self.define_tasks()
        self.assertInterpretEqual(Task.get("B@Loading").interpret(), {
            "name": "B@Loading",
            "next": ["B@Loading", "Other", "B"],
        })

    def test_4(self):
        self.define_tasks()
        self.assertInterpretEqual(Task.get("Loading").interpret(), {
            "name": "Loading",
            "next": ["Loading"],
        })

    def test_5(self):
        self.define_tasks()
        self.assertTaskEqual(Task.get("B@Loading"), {
            "name": "B@Loading",
            "next": ["B#self", "B#next", "B#back"],
        })
