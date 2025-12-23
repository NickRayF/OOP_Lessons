import re
from itertools import product
from typing import List, Dict, Any, Optional


class LogicExpressionEvaluator:
    
    @staticmethod
    def safe_eval(expression: str, variables: Dict[str, bool]) -> bool:
        try:
            safe_env = {
                'and': lambda x, y: x and y,
                'or': lambda x, y: x or y,
                'not': lambda x: not x,
                'True': True,
                'False': False,
            }
            safe_env.update(variables)
            return bool(eval(expression, {"__builtins__": {}}, safe_env))
        except Exception:
            raise ValueError(f"Ошибка вычисления выражения: {expression}")


class VariableExtractor:
    
    @staticmethod
    def extract(expression: str) -> List[str]:
        reserved_words = {'and', 'or', 'not', 'True', 'False'}
        found_tokens = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', expression)
        unique_vars = sorted(list(set(token for token in found_tokens if token not in reserved_words)))
        return unique_vars


class TruthTableGenerator:
    
    def __init__(self):
        self.table_data = []
        self.expression_string = ""
        self.variable_list = []
        self.evaluator = LogicExpressionEvaluator()
        self.extractor = VariableExtractor()

    def generate_table(self, expression: str) -> List[Dict[str, Any]]:
        self.expression_string = expression
        self.variable_list = self.extractor.extract(expression)
        
        if not self.variable_list:
            raise ValueError("В выражении не найдено переменных")

        self.table_data = []
        variable_count = len(self.variable_list)

        for combination in product([0, 1], repeat=variable_count):
            value_map = dict(zip(self.variable_list, combination))
            
            try:
                evaluation_result = self.evaluator.safe_eval(expression, value_map)
                row_data = value_map.copy()
                row_data['result'] = evaluation_result
                self.table_data.append(row_data)
            except Exception as e:
                raise ValueError(f"Ошибка при значениях {value_map}: {str(e)}")

        return self.table_data

    def get_filtered_data(self, filter_kind: str = 'all') -> List[Dict[str, Any]]:
        if filter_kind == 'all':
            return self.table_data
        elif filter_kind == 'true':
            return [row for row in self.table_data if row['result']]
        elif filter_kind == 'false':
            return [row for row in self.table_data if not row['result']]
        elif filter_kind == 'minority':
            true_rows = sum(1 for row in self.table_data if row['result'])
            false_rows = len(self.table_data) - true_rows
            
            if true_rows < false_rows:
                return [row for row in self.table_data if row['result']]
            elif false_rows < true_rows:
                return [row for row in self.table_data if not row['result']]
            else:
                return self.table_data
        return self.table_data

    def get_table_statistics(self) -> Dict[str, Any]:
        if not self.table_data:
            return {}

        true_count = sum(1 for row in self.table_data if row['result'])
        total_count = len(self.table_data)
        false_count = total_count - true_count

        minority_status = 'True' if true_count < false_count else 'False' if false_count < true_count else 'Equal'

        return {
            'total_rows': total_count,
            'true_rows': true_count,
            'false_rows': false_count,
            'minority_status': minority_status
        }

    def build_expression_from_table(self, custom_data: Optional[List[Dict[str, Any]]] = None) -> str:
        data_to_use = custom_data or self.table_data
        true_rows = [row for row in data_to_use if row['result']]

        if not true_rows:
            return "False"
        if len(true_rows) == len(data_to_use):
            return "True"

        expression_parts = []
        for row in true_rows:
            term_components = []
            for var_name in self.variable_list:
                if row[var_name]:
                    term_components.append(var_name)
                else:
                    term_components.append(f"not {var_name}")
            expression_parts.append(f"({' and '.join(term_components)})")

        return " or ".join(expression_parts)


class EGETaskSolver:
    
    def __init__(self):
        self.generator = TruthTableGenerator()

    def find_variable_mapping(self, expression: str, partial_table: List[Dict[str, Any]]) -> List[str]:
        variable_names = sorted(self.generator.extractor.extract(expression))
        
        if len(variable_names) != 4:
            raise ValueError(f"Нужно 4 переменные, найдено: {variable_names}")

        complete_table = []
        for x1, x2, x3, x4 in product([0, 1], repeat=4):
            value_assignment = {
                variable_names[0]: x1,
                variable_names[1]: x2,
                variable_names[2]: x3,
                variable_names[3]: x4
            }
            result_value = self.generator.evaluator.safe_eval(expression, value_assignment)
            
            row_info = value_assignment.copy()
            row_info['result'] = result_value
            complete_table.append(row_info)

        column_labels = ['F1', 'F2', 'F3', 'F4']
        found_solutions = []

        for var_permutation in product(variable_names, repeat=4):
            if len(set(var_permutation)) != 4:
                continue
                
            target_result_value = partial_table[0]['result']
            matching_rows = [row for row in complete_table if row['result'] == target_result_value]

            if len(matching_rows) < len(partial_table):
                continue

            for row_permutation in product(matching_rows, repeat=len(partial_table)):
                if len(set(row_permutation)) != len(partial_table):
                    continue
                    
                mapping_valid = True
                for idx, problem_row in enumerate(partial_table):
                    candidate_row = row_permutation[idx]

                    for col_idx, col_label in enumerate(column_labels):
                        mapped_variable = var_permutation[col_idx]
                        problem_value = problem_row[col_label]
                        candidate_value = candidate_row[mapped_variable]

                        if problem_value is not None and problem_value != candidate_value:
                            mapping_valid = False
                            break
                    if not mapping_valid:
                        break

                if mapping_valid:
                    solution_string = "".join(var_permutation)
                    if solution_string not in found_solutions:
                        found_solutions.append(solution_string)

        return found_solutions


class TruthTableCalculator:
    
    def __init__(self):
        self.generator = TruthTableGenerator()
        self.solver = EGETaskSolver()

    def calculate(self, expression: str) -> List[Dict[str, Any]]:
        return self.generator.generate_table(expression)

    def get_filtered_results(self, filter_type: str = 'all') -> List[Dict[str, Any]]:
        return self.generator.get_filtered_data(filter_type)

    def get_stats(self) -> Dict[str, Any]:
        return self.generator.get_table_statistics()

    def create_expression_from_table(self, custom_results: Optional[List[Dict[str, Any]]] = None) -> str:
        return self.generator.build_expression_from_table(custom_results)

    def solve_ege_task(self, expression: str, incomplete_table: List[Dict[str, Any]]) -> List[str]:
        return self.solver.find_variable_mapping(expression, incomplete_table)

    def _extract_variables(self, expression: str) -> List[str]:
        return self.generator.extractor.extract(expression)