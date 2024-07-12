import unittest

from tools.TasksCommandTool.task import Task, _ALL_TASKS
from .utils import test_info_a, test_pipeline_a, test_pipeline_b, test_virtual_task, test_match_template_a


class TaskTest(unittest.TestCase):

    def tearDown(self):
        _ALL_TASKS.clear()

    def test_template_task_inheritance(self):
        Task("A", test_pipeline_a)
        task = Task._build_template_task("B@A")
        self.assertEqual(task.task_dict, {
            "sub": ["B@A_sub", "B@A_sub2"],
            "next": ["B@A_next"],
            "onErrorNext": ["B@A_onErrorNext"],
            "exceededNext": ["B@A_exceededNext"],
            "reduceOtherTimes": ["B@A_reduceOtherTimes"],
        })

    def test_nested_template_task_inheritance(self):
        Task("A", test_pipeline_a)
        Task("B", test_pipeline_b)
        task = Task._build_template_task("C@B@A")
        self.assertEqual(_ALL_TASKS["B@A"].task_dict, {
            "sub": ["B@A_sub", "B@A_sub2"],
            "next": ["B@A_next"],
            "onErrorNext": ["B@A_onErrorNext"],
            "exceededNext": ["B@A_exceededNext"],
            "reduceOtherTimes": ["B@A_reduceOtherTimes"],
        })
        self.assertEqual(task.task_dict, {
            "sub": ["C@B@A_sub", "C@B@A_sub2"],
            "next": ["C@B@A_next"],
            "onErrorNext": ["C@B@A_onErrorNext"],
            "exceededNext": ["C@B@A_exceededNext"],
            "reduceOtherTimes": ["C@B@A_reduceOtherTimes"],
        })

    def test_template_task_with_override(self):
        Task("A", test_pipeline_a)
        Task("B", test_pipeline_b)
        Task("B@A", {
            "sub": ["no_new_sub", "no_new_sub2"],
            "next": ["no_new_next"],
            "onErrorNext": ["no_new_onErrorNext"],
            "exceededNext": ["no_new_exceededNext"],
            "reduceOtherTimes": ["no_new_reduceOtherTimes"],
        })
        task = Task._build_template_task("C@B@A")
        self.assertEqual(task.task_dict, {
            "sub": ["C@no_new_sub", "C@no_new_sub2"],
            "next": ["C@no_new_next"],
            "onErrorNext": ["C@no_new_onErrorNext"],
            "exceededNext": ["C@no_new_exceededNext"],
            "reduceOtherTimes": ["C@no_new_reduceOtherTimes"],
        })

    def test_virtual_task(self):
        Task("virtual", test_virtual_task)
        task = Task._build_template_task("B@virtual")
        self.assertEqual(task.task_dict, {
            "sub": ["B#virtual_sub", "B#virtual_sub2"],
            "next": ["B#virtual_next"],
            "onErrorNext": ["B#virtual_onErrorNext"],
            "exceededNext": ["B#virtual_exceededNext"],
        })

    def test_algorithm_override(self):
        Task("A", {**test_pipeline_a, **test_match_template_a})
        Task("B@A", {
            "algorithm": "OcrDetect",
        })
        task = Task._build_template_task("B@A")
        self.assertEqual(task.task_dict, {
            "sub": ["B@A_sub", "B@A_sub2"],
            "next": ["B@A_next"],
            "onErrorNext": ["B@A_onErrorNext"],
            "exceededNext": ["B@A_exceededNext"],
            "reduceOtherTimes": ["B@A_reduceOtherTimes"],
            "algorithm": "OcrDetect",
        })