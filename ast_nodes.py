# This file includes the definitions of the Node classes to build the AST tree.
# The initial grammar program -> declarations stmt_block can be split into two individual parts:
# 1. The declarations part is handled mid-parsing, in the parser file we build the symbol_table that includes a
# dictionary with all the identifiers and their type.
# 2. the stmt_block part is handled after the parsing step is complete, we use code_gen functions to generate the quad
# code while also doing semantic analysis for the identifiers.
from sys import stderr
from header import *


class ProgramNode:
    def __init__(self, declarations, stmt_block):
        self.declarations = declarations
        self.stmt_block = stmt_block

    def code_gen(self):
        return self.stmt_block.code_gen() + "HALT\n"


class DeclarationsNode:
    def __init__(self):
        self.declarations = []

    def add_declaration(self, declaration):
        self.declarations.append(declaration)


class DeclarationNode:
    def __init__(self, idlist, idtype):
        self.idList = idlist
        self.idtype = idtype


class TypeNode:
    def __init__(self, idtype):
        self.idtype = idtype


class IdListNode:
    def __init__(self):
        self.ids = []

    def add_id(self, identifier):
        self.ids.append(identifier)


class StmtNode:
    def __init__(self, stmt):
        self.stmt = stmt

    def code_gen(self):
        return self.stmt.code_gen()


class AssignmentStmtNode:
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def code_gen(self):
        if self.identifier in symbol_table:
            if isinstance(self.expression, ExpressionNode):
                self.expression.parent_id = self.identifier
            expression_type = symbol_table[self.identifier]
            expression_code = self.expression.code_gen()
            # If the parent id was used by the son , it means that the expression had addop , mulop or was a cast
            if not self.expression.parent_id_used:
                return f'{"RASN" if expression_type == "float" else "IASN"} {self.identifier} {expression_code}'
            else:
                return expression_code
        else:
            stderr.write(f"Semantic Error, Identifier {self.identifier} wasn't defined.")


class InputStmtNode:
    def __init__(self, identifier):
        self.identifier = identifier

    def code_gen(self):
        if self.identifier in symbol_table:
            if symbol_table[self.identifier] == "float":
                return f"RINP {self.identifier}"
            else:
                return f"IINP {self.identifier}"
        else:
            stderr.write(f"Semantic Error, Identifier {self.identifier} wasn't defined.")


class OutputStmtNode:
    def __init__(self, expression):
        self.expression = expression

    def code_gen(self):
        expression_code = self.expression.code_gen()
        exp_type = self.expression.exp_type
        # If the expression had a temp it means that the expression had more than 2 operations
        # and it used temp while converting the code to the quad language
        if self.expression.temp is not None:
            return f'{expression_code}\n {"R" if exp_type == "float" else "I"}PRT {self.expression.temp}'
        else:
            return f'{"R" if exp_type == "float" else "I"}PRT {self.expression.code_gen()}'


class IfStmtNode:
    def __init__(self, boolexpr, true_stmt, false_stmt):
        self.boolexpr = boolexpr
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt

    def code_gen(self):
        boolexpr_code = self.boolexpr.code_gen()
        true_stmt_code = self.true_stmt.code_gen()
        false_stmt_code = self.false_stmt.code_gen()
        label_false = gen_label()
        label_exit = gen_label()
        # Replace the labels we jump to if the statement is not
        if (type(self.boolexpr)) == NotExprNode:
            return (f"{boolexpr_code}\nJMPZ {label_false} {self.boolexpr.temp}\n"
                f"{false_stmt_code}\nJUMP {label_exit}\n{label_false}:\n{true_stmt_code:}\n{label_exit}:")
        else:
            return (f"{boolexpr_code}\nJMPZ {label_false} {self.boolexpr.temp}\n"
                    f"{true_stmt_code}\nJUMP {label_exit}\n{label_false}:\n{false_stmt_code:}\n{label_exit}:")


class WhileStmtNode:
    def __init__(self, boolexpr, stmt):
        self.boolexpr = boolexpr
        self.stmt = stmt

    def code_gen(self):
        label_entry = gen_label()
        label_exit = gen_label()
        boolexpr_code = self.boolexpr.code_gen()
        stmt_code = self.stmt.code_gen()
        # Returns the while code while matching the labels at the right place according to the boolean expression
        return f"{label_entry}:\n{boolexpr_code}\nJMPZ {label_exit} {self.boolexpr.temp} \n{stmt_code}JUMP {label_entry}\n{label_exit}:"


class StmtBlockNode:
    def __init__(self, stmtlist):
        self.stmtlist = stmtlist

    def code_gen(self):
        return self.stmtlist.code_gen()


class StmtListNode:
    def __init__(self):
        self.stmts = []

    def add_stmt(self, stmt):
        self.stmts.append(stmt)

    def code_gen(self):
        stmts_code = ""
        for stmt in self.stmts:
            stmts_code += stmt.code_gen() + "\n"
        return stmts_code


class OrExprNode:
    def __init__(self, boolterm1, boolterm2=None, temp=None):
        self.boolterm1 = boolterm1
        self.boolterm2 = boolterm2
        self.temp = temp

    def code_gen(self):
        boolterm1_code = self.boolterm1.code_gen()
        if self.boolterm2 is not None:
            boolterm2_code = self.boolterm2.code_gen()
            boolterm1_temp = self.boolterm1.temp
            boolterm2_temp = self.boolterm2.temp
            self.temp = gen_temp()
            label_or = gen_label()
            label_assign_true = gen_label()
            label_assign_false = gen_label()
            label_exit = gen_label()
            # Add labels to jump between the booleans expression in the following way:
            # if the first expression is true it jumps to the "True" part. Otherwise,
            # it jumps to the second boolean expression . if the second expression is true
            # it jumps to the "True" part but otherwise it skips goes false
            return (
                f"{boolterm1_code}\nJMPZ {label_or} {boolterm1_temp}\nJMP {label_assign_true}\n{label_or}:\n"
                f"{boolterm2_code}\nJMPZ {label_assign_false} {boolterm2_temp}\n{label_assign_true}:\nIASN "
                f"{self.temp} 1\nJMP {label_exit}\n{label_assign_false}:\nIASN {self.temp} 0 \n{label_exit}:")
        # if there's no boolterm2 the rule was '''boolexpr : boolterm'''
        else:
            self.temp = self.boolterm1.temp
            return boolterm1_code


class AndExprNode:
    def __init__(self, boolfactor1, boolfactor2=None, temp=None):
        self.boolfactor1 = boolfactor1
        self.boolfactor2 = boolfactor2
        self.temp = temp

    def code_gen(self):
        boolfactor1_code = self.boolfactor1.code_gen()
        if self.boolfactor2 is not None:
            boolfactor2_code = self.boolfactor2.code_gen()
            boolfactor1_temp = self.boolfactor1.temp
            boolfactor2_temp = self.boolfactor2.temp
            self.temp = gen_temp()
            label_false = gen_label()
            label_skip_false = gen_label()
            # Add labels to jump between the booleans expression in the following way:
            # if the first expression is true it jumps to the second boolean expression to check it. Otherwise,
            # it jumps to "False" part . if the second expression is true it continues to the "True" part ,
            # after that it jumps to skip the "False" part. Otherwise, it jumps straight to the "False" part.
            return (f"{boolfactor1_code}\nJMPZ {label_false} {boolfactor1_temp}\n{boolfactor2_code}\nJMPZ {label_false} {boolfactor2_temp}\n"
                    f"IASN {self.temp} 1 \nJUMP {label_skip_false}\n{label_false}:\nIASN {self.temp} 0\n{label_skip_false}:")
        # if there's no boolterm2 the rule was '''boolterm : boolfactor''''''
        else:
            self.temp = self.boolfactor1.temp
            return boolfactor1_code


class NotExprNode:
    def __init__(self, boolexpr, temp=None):
        self.boolexpr = boolexpr
        self.temp = temp

    def code_gen(self):
        # Stimulates not expression in the boolexpr node by replacing the location of the labels
        boolexpr_code = self.boolexpr.code_gen()
        self.temp = self.boolexpr.temp
        return boolexpr_code


class RelExprNode:
    def __init__(self, expression1, relop, expression2, temp=None, exp_type=None ):
        self.expression1 = expression1
        self.relop = relop
        self.expression2 = expression2
        self.temp = temp
        self.exp_type = exp_type

    def code_gen(self):
        expression1_code = self.expression1.code_gen()
        expression2_code = self.expression2.code_gen()
        self.temp = gen_temp()
        self.exp_type = get_expression_type(self.expression1.exp_type, self.expression2.exp_type)
        if self.relop == '==' or self.relop == '<' or self.relop == '>' or self.relop == '!=':
            relop_code = self.handle_relop_with_one_operations(expression1_code, expression2_code,
                                    self.expression1.temp, self.expression2.temp, self.relop, self.temp, self.exp_type)
        # relop is >= or <=
        else:
            relop_code = self.handle_relop_with_two_operations(expression1_code, expression2_code,
                                                    self.expression1.temp, self.expression2.temp, self.relop, self.temp, self.exp_type)
        return relop_code

    # Handles the relops < , > , == , !=
    @staticmethod
    def handle_relop_with_one_operations(expression1_code, expression2_code, expression1_temp, expression2_temp, relop, temp, exp_type):
        temp_string = "R" if exp_type == 'float' else "I"
        if relop == '<':
            temp_string += f"LSS {temp}"
        elif relop == '>':
            temp_string += f"GRT {temp}"
        elif relop == '==':
            temp_string += f"EQL {temp}"
        else:
            temp_string += f"NQL {temp}"
        # creates the matching output according to the expressions results
        # if the expression created temps it used those temps with the relop operation
        if expression1_temp is not None and expression2_temp is not None:
            return f"{expression1_code} \n{temp_string} {expression1_temp} {expression2_temp} \n{expression2_code}"
        elif expression1_temp is not None:
            return f"{expression1_code}\n{temp_string} {expression1_temp} {expression2_code}"
        elif expression2_temp is not None:
            return f"{temp_string} {expression1_code} {expression2_temp} \n{expression2_code}"
        else:
            return f"{temp_string} {expression1_code} {expression2_code}"

    # Handles the relops <= , >=
    @staticmethod
    def handle_relop_with_two_operations(expression1_code, expression2_code, expression1_temp, expression2_temp, relop, temp, exp_type):
        boolexp1_code = RelExprNode.handle_relop_with_one_operations(expression1_code, expression2_code, expression1_temp,
                                                    expression2_temp, "=", temp, exp_type)
        if relop == "<=":
            boolexp2_code = RelExprNode.handle_relop_with_one_operations(expression1_code, expression2_code, expression1_temp, expression2_temp, "<", temp, exp_type)
        else:
            boolexp2_code = RelExprNode.handle_relop_with_one_operations(expression1_code, expression2_code, expression1_temp, expression2_temp, ">", temp, exp_type)
        label_or = gen_label()
        label_assign_true = gen_label()
        label_assign_false = gen_label()
        label_exit = gen_label()
        # Stimulates a boolean expression, for example , a <= b as a < b and a = b.
        # It does that by using jumps the same way as we did in the "And" boolean expression
        return (
            f"{boolexp1_code}\nJMPZ {label_or}\n{boolexp1_code}\nJMP {label_assign_true}\n{label_or}:\n"
            f"{boolexp2_code}\nJMPZ {label_assign_false}\n{boolexp2_code}\n{label_assign_true}:\nIASN "
            f"{temp} 1\nJMP {label_exit}\n{label_assign_false}:\nIASN {temp} 0 \n{label_exit}:")


class ExpressionNode:
    def __init__(self, left, addop=None, right=None, temp=None, exp_type=None, parent_id = None, parent_id_used = None):
        self.left = left
        self.addop = addop
        self.right = right
        self.temp = temp
        self.exp_type = exp_type
        self.parent_id = parent_id
        self.parent_id_used = False

    def code_gen(self):
        if self.addop is not None:
            left_code = self.left.code_gen()
            right_code = self.right.code_gen()
            self.exp_type = get_expression_type(self.left.exp_type, self.right.exp_type)
            temp_string = "R" if self.exp_type == 'float' else "I"
            temp_string = (temp_string+"ADD" if self.addop == '+' else temp_string+"SUB")
            # if there's no parent_id it means the expression didn't come from an assignment node
            if self.parent_id is None:
                self.temp = gen_temp()
                temp_string = temp_string + f" {self.temp}"
            # set the parent_id_used to True so we know the assignment operation was addop
            else:
                temp_string = temp_string + f" {self.parent_id}"
                self.parent_id_used = True
            # creates the code depending on the temps created from left and right expression
            if self.left.temp is not None and self.right.temp is not None:
                return f"{left_code}\n{right_code}\n{temp_string} {self.left.temp} {self.right.temp}"
            elif self.left.temp is not None:
                return f"{left_code}\n{temp_string} {self.left.temp} {right_code}"
            elif self.right.temp is not None:
                return f"{temp_string} {left_code} {self.right.temp}\n{right_code}"
            else:
                return f"{temp_string} {left_code} {right_code}"
        # if there's no addop the used rule was '''expression : term'''
        else:
            self.left.parent_id = self.parent_id
            left_code = self.left.code_gen()
            self.temp = self.left.temp
            self.exp_type = self.left.exp_type
            self.parent_id_used = self.left.parent_id_used
            return left_code


class TermNode:
    def __init__(self, left, mulop=None, right=None, temp=None, exp_type=None, parent_id = None, parent_id_used = None ):
        self.left = left
        self.mulop = mulop
        self.right = right
        self.temp = temp
        self.exp_type = exp_type
        self.parent_id = parent_id
        self.parent_id_used = False

    def code_gen(self):
        if self.mulop is not None:
            left_code = self.left.code_gen()
            right_code = self.right.code_gen()
            self.exp_type = get_expression_type(self.left.exp_type,self.right.exp_type)
            temp_string = "R" if self.exp_type == 'float' else "I"
            temp_string = (temp_string + "MLT" if self.mulop == '*' else temp_string + "DIV")
            # if there's no parent_id it means the expression didn't come from an assignment node
            if self.parent_id is None:
                self.temp = gen_temp()
                temp_string = temp_string + f" {self.temp}"
            # set the parent_id_used to True so we know the assignment operation was mulop
            else:
                temp_string = temp_string + f" {self.parent_id}"
                self.parent_id_used = True
            # creates the code depending on the temps created from left and right expression
            if self.left.temp is not None and self.right.temp is not None:
                return f"{left_code} \n{right_code}\n{temp_string} {self.left.temp} {self.right.temp}"
            elif self.left.temp is not None:
                return f"{left_code}\n {temp_string} {self.left.temp} {right_code}"
            elif self.right.temp is not None:
                return f"{temp_string} {left_code} {self.right.temp} \n{right_code}"
            else:
                return f"{temp_string} {left_code} {right_code}"
        # if there's no mulop the used rule was '''term : factor'''
        else:
            # checks if the son is a cast to pass the parent id. also,cast always uses the parent id
            # so it sets the variable to true
            if isinstance(self.left,CastFloatExpressionNode) or isinstance(self.left,CastIntExpressionNode):
                self.left.parent_id = self.parent_id
                self.parent_id_used = True
            left_code = self.left.code_gen()
            self.temp = self.left.temp
            self.exp_type = self.left.exp_type
            return left_code


class FactorNode:
    def __init__(self, attribute, exp_type=None):
        self.attribute = attribute
        self.temp = None
        self.exp_type = exp_type

    def code_gen(self):
        # sets the type of the expression to integer or float according to the attribute.
        # uses the expression type to know what code output to use in the quad language
        self.exp_type = self.is_integer_or_float(self.attribute)
        return f"{self.attribute}"

    @staticmethod
    def is_integer_or_float(attribute):
        # checks the type of the attribute
        if isinstance(attribute, int):
            return "int"
        elif isinstance(attribute, float):
            return "float"
        else:
            return symbol_table[attribute]


class CastIntExpressionNode:
    def __init__(self, expression, temp=None, exp_type=None, parent_id=None):
        self.expression = expression
        self.temp = temp
        self.exp_type = exp_type
        self.parent_id = parent_id

    def code_gen(self):
        expression_code = self.expression.code_gen()
        self.temp = self.expression.temp
        self.exp_type = "int"
        # if the expression used temp it will use that temp in the cast output. otherwise,
        # it means that the expression was an id or number so it will use that.
        if self.temp is None:
            temp_code = "RTOI " + self.parent_id + " " + expression_code
        else:
            temp_code = expression_code + "\n" + "RTOI " + self.parent_id + " " + self.temp
        return temp_code


class CastFloatExpressionNode:
    def __init__(self, expression, temp=None, exp_type=None, parent_id=None):
        self.expression = expression
        self.temp = temp
        self.exp_type = exp_type
        self.parent_id = parent_id

    def code_gen(self):
        expression_code = self.expression.code_gen()
        self.temp = self.expression.temp
        self.exp_type = "float"
        # if the expression used temp it will use that temp in the cast output. otherwise,
        # it means that the expression was an id or number so it will use that.
        if self.temp is None:
            temp_code = "ITOR " + self.parent_id + " " + expression_code
        else:
            temp_code = expression_code + "\n" + "RTOI " + self.parent_id + " " +  self.temp
        return temp_code


