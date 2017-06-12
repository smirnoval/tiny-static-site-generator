"""Simple template engine."""
import re
import operator
import ast
from template_engine.exceptions import TemplateError
from template_engine.exceptions import TemplateContextError, TemplateSyntaxError
from template_engine.exceptions import TemplateInheritanceError, TemplateLoopInheritanceError


def flatten(input_list):
    output_list = []
    for element in input_list:
        if type(element) == list:
            output_list.extend(flatten(element))
        else:
            output_list.append(element)
    return output_list


PAGE_TOKEN_START = '{!'
PAGE_TOKEN_END = '!}'
PAGE_REGEX = re.compile(r"(%s.*?%s)" % (
    PAGE_TOKEN_START,
    PAGE_TOKEN_END
))

PAGE_BLOCK_START = '{?'
PAGE_BLOCK_END = '?}'
PAGE_BLOCKS_REGEX = re.compile(r"({\?.*?\?})")

INCLUDE_TAG_START = '{#'
INCLUDE_TAG_END = '#}'
INCLUDE_TAGS_REGEX = re.compile(r"(%s.*?%s)" % (
    INCLUDE_TAG_START,
    INCLUDE_TAG_END
))

VARIABLE_TOKEN_START = '{{'
VARIABLE_TOKEN_END = '}}'
BLOCK_TOKEN_START = '{%'
BLOCK_TOKEN_END = '%}'
TOKEN_REGEX = re.compile(r"(%s.*?%s|%s.*?%s)" % (
    VARIABLE_TOKEN_START,
    VARIABLE_TOKEN_END,
    BLOCK_TOKEN_START,
    BLOCK_TOKEN_END
))

VARIABLE_FRAGMENT = 0
OPEN_BLOCK_FRAGMENT = 1
CLOSE_BLOCK_FRAGMENT = 2
TEXT_FRAGMENT = 3

WHITESPACE = re.compile('\s+')

OPERATOR_TABLE = {
    '<': operator.lt,
    '>': operator.gt,
    '==': operator.eq,
    '!=': operator.ne,
    '<=': operator.le,
    '>=': operator.ge
}


def eval_expression(expr):
    """Check if expression is Python expression."""
    try:
        return 'literal', ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        return 'name', expr


def resolve(name, context):
    """Resolve syntax substintion."""
    if name.startswith('..'):
        context = context.get('..', {})
        name = name[2:]
    try:
        for tok in name.split('.'):
            if tok in context.keys():
                context = context[tok]
            else:
                context = ''
        return context
    except KeyError:
        raise TemplateContextError(name)


class Fragment:
    """Fragment of template which used for definition of tokens."""

    def __init__(self, raw_text):
        self.raw = raw_text
        self.clean = self.clean_fragment()

    def clean_fragment(self):
        """Delete trash from fragment."""
        if self.raw[:2] in (VARIABLE_TOKEN_START, BLOCK_TOKEN_START):
            return self.raw[2:-2].strip()
        return self.raw

    @property
    def type(self):
        """Determine the type of the fragment."""
        raw_start = self.raw[:2]
        if raw_start == VARIABLE_TOKEN_START:
            return VARIABLE_FRAGMENT
        elif raw_start == BLOCK_TOKEN_START:
            return CLOSE_BLOCK_FRAGMENT if self.clean[:3] == 'end' else OPEN_BLOCK_FRAGMENT
        else:
            return TEXT_FRAGMENT


class Node:
    """Element of tree."""

    creates_scope = False

    def __init__(self, fragment=None):
        self.children = []
        self.process_fragment(fragment)

    def process_fragment(self, fragment):
        pass

    def enter_scope(self):
        pass

    def render(self, context):
        pass

    def exit_scope(self):
        pass

    def render_children(self, context, children=None):
        """Render contex info into html."""
        if children is None:
            children = self.children

        def render_child(child):
            child_html = child.render(context)
            return '' if not child_html else str(child_html)
        return ''.join(map(render_child, children))


class Root(Node):
    """Root of tree."""

    def render(self, context):
        """Start render of elements."""
        return self.render_children(context)


class Variable(Node):
    """Python-like variables."""

    def process_fragment(self, fragment):
        self.name = fragment

    def render(self, context):
        return resolve(self.name, context)


class Array(Node):
    """Array of elements."""

    creates_scope = True

    def process_fragment(self, fragment):
        try:
            _, item = WHITESPACE.split(fragment, 1)
            self.item = eval_expression(item)
        except ValueError:
            raise TemplateSyntaxError(fragment)

    def render(self, context):
        items = self.item[1] if self.item[0] == 'literal' else resolve(self.item[1], context)

        def render_item(item):
            return self.render_children({'..': context, 'item': item})
        return ''.join(map(render_item, items))


class If(Node):
    """'If' instruction."""

    creates_scope = True

    def process_fragment(self, fragment):
        bits = fragment.split()[1:]
        if len(bits) not in (1, 3):
            raise TemplateSyntaxError(fragment)
        self.lhs = eval_expression(bits[0])
        if len(bits) == 3:
            self.op = bits[1]
            self.rhs = eval_expression(bits[2])

    def render(self, context):
        lhs = self.resolve_side(self.lhs, context)
        if hasattr(self, 'op'):
            op = OPERATOR_TABLE.get(self.op)
            if op is None:
                raise TemplateSyntaxError(self.op)
            rhs = self.resolve_side(self.rhs, context)
            exec_if_branch = op(lhs, rhs)
        else:
            exec_if_branch = operator.truth(lhs)
        if_branch, else_branch = self.split_children()
        return self.render_children(context, self.if_branch if exec_if_branch else self.else_branch)

    def resolve_side(self, side, context):
        return side[1] if side[0] == 'literal' else resolve(side[1], context)

    def exit_scope(self):
        self.if_branch, self.else_branch = self.split_children()

    def split_children(self):
        if_branch, else_branch = [], []
        curr = if_branch
        for child in self.children:
            if isinstance(child, Else):
                curr = else_branch
                continue
            curr.append(child)
        return if_branch, else_branch


class Else(Node):
    """'Else' instruction."""

    def render(self, context):
        pass


class Text(Node):
    """All what not instruction."""

    def process_fragment(self, fragment):
        self.text = fragment

    def render(self, context):
        return self.text


class Compiler:
    """Find, process and compile all instructions in template."""

    def __init__(self, template_string):
        self.template_string = template_string

    def each_fragment(self):
        for fragment in TOKEN_REGEX.split(self.template_string):
            if fragment:
                yield Fragment(fragment)

    def compile(self):
        root = Root()
        scope_stack = [root]
        for fragment in self.each_fragment():
            if not scope_stack:
                raise TemplateError('nesting issues')
            parent_scope = scope_stack[-1]
            if fragment.type == CLOSE_BLOCK_FRAGMENT:
                parent_scope.exit_scope()
                scope_stack.pop()
                continue
            new_node = self.create_node(fragment)
            if new_node:
                parent_scope.children.append(new_node)
                if new_node.creates_scope:
                    scope_stack.append(new_node)
                    new_node.enter_scope()
        return root

    def create_node(self, fragment):
        node_class = None
        if fragment.type == TEXT_FRAGMENT:
            node_class = Text
        elif fragment.type == VARIABLE_FRAGMENT:
            node_class = Variable
        elif fragment.type == OPEN_BLOCK_FRAGMENT:
            cmd = fragment.clean.split()[0]
            if cmd == 'array':
                node_class = Array
            elif cmd == 'if':
                node_class = If
            elif cmd == 'else':
                node_class = Else
        if node_class is None:
            raise TemplateSyntaxError(fragment)
        return node_class(fragment.clean)


class Template:

    def __init__(self, contents):
        self.contents = contents
        self.root = Compiler(contents).compile()

    def render(self, **kwargs):
        return self.root.render(kwargs)


class Collector:
    """Collect all nested templates, then transmit them to Template."""

    def __init__(self, absolute_path, pagename):
        self.path = absolute_path
        self.pagename = pagename
        self.collected_page = [pagename]
        with open(self.path + self.pagename, 'r') as file:
            self.file = str(file.read())

    def __str__(self):
        return self.file

    def assemble_page(self, **kwargs):
        self.prepare_page()
        self.file = self.prepare_include_tags()
        rendered = Template(str(self.file)).render(**kwargs)
        return rendered

    def prepare_include_tags(self, text=None):
        if text:
            include_tags = [x for x in INCLUDE_TAGS_REGEX.split(text) if x]
        else:
            include_tags = [x for x in INCLUDE_TAGS_REGEX.split(self.file) if x]
        if len(include_tags) == 1 and text is None:
            return ''.join(flatten(include_tags))
        elif len(include_tags) == 1:
            return include_tags
        tags = []
        for i in range(len(include_tags)):
            if include_tags[i][:2] == "{#" and include_tags[i][-2:] == "#}":
                cur = include_tags[i][2:-2].strip()
                tags.append([cur, i])
        for i in range(len(tags)):
            text = self.find_parent_data(tags[i][0])
            res = self.prepare_include_tags(text)
            include_tags[tags[i][1]] = res
        return ''.join(flatten(include_tags))

    def prepare_page(self, previous_blocks=None):
        if previous_blocks is not None:
            self.file = self.find_blocks_for_substition(previous_blocks)
        components = [x.strip() for x in PAGE_REGEX.split(str(self.file)) if x]
        if len(components) == 1:
            return
        elif len(components) == 2:
            parent_address = components[0][2:-2].strip().strip('"').strip("'")
            if parent_address not in self.collected_page:
                self.collected_page.append(parent_address)
            else:
                raise TemplateLoopInheritanceError
            blocks = self.find_blocks(components[1])
            self.file = self.find_parent_data(parent_address)
            self.prepare_page(blocks)
        else:
            raise TemplateInheritanceError

    def find_blocks(self, raw_blocks):
        blocks = [x for x in PAGE_BLOCKS_REGEX.split(raw_blocks) if x]
        stack = []
        dic = {}
        for i in range(len(blocks)):
            if blocks[i][:2] == '{?' and 'endblock' not in blocks[i]:
                cur = blocks[i][2:-2].strip()
                stack.append([cur, i])
            elif blocks[i][:2] == '{?' and 'endblock' in blocks[i]:
                if len(stack) == 0:
                    raise TemplateSyntaxError
                start = stack.pop()
                dic[start[0]] = [blocks[x] for x in range(start[1] + 1, i)]
        return dic

    def find_blocks_for_substition(self, subs):
        components = [x for x in PAGE_BLOCKS_REGEX.split(str(self.file)) if x]
        stack = []
        dic = {}
        for i in range(len(components)):
            if components[i][:2] == '{?' and 'endblock' not in components[i]:
                cur = components[i][2:-2].strip()
                stack.append([cur, i])
            elif components[i][:2] == '{?' and 'endblock' in components[i]:
                if len(stack) == 0:
                    raise TemplateSyntaxError
                start = stack.pop()
                dic[start[0]] = list(range(start[1], i + 1))
        for i in dic.keys():
            if i in subs.keys():
                for j in dic[i]:
                    components[j] = ''
                components[dic[i][0]] = "".join(subs[i])
        return "".join(components)

    def find_parent_data(self, parent_name):
        with open(self.path + '/' + parent_name, 'r') as file:
            return str(file.read())


if __name__ == "__main__":
    print("Base.py")
