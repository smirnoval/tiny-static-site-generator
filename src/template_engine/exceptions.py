"""Exceptions of 'simple-template-engine'."""
import logging


class TemplateError(Exception):
    """Main template error."""

    def __init__(self):
        logging.warning('Template error!')


class TemplateContextError(TemplateError):
    """Wrong context, not given context instructions."""

    def __init__(self, context):
        super().__init__()
        self.context = context
        logging.warning('Template context error!')

    def __str__(self):
        return 'Cannot resolve {0}'.format(self.context_var)


class TemplateSyntaxError(TemplateError):
    """Wrong syntax."""

    def __init(self, syntax_error):
        super().__init__()
        self.syntax_error = syntax_error
        logging.warning('Template syntax error!')

    def __str__(self):
        return 'Invalid syntax {0}'.format(self.syntax_error)


class TemplateInheritanceError(TemplateError):
    """Multiple inheritance."""

    def __init(self, inheritance_error):
        super().__init__()
        self.inheritance_error = inheritance_error
        logging.warning('Template inheritance error!')

    def __str__(self):
        return 'Invalid inheritance {0}'.format(self.inheritance_error)


class TemplateLoopInheritanceError(TemplateError):
    """Inheritance loop."""

    def __init(self, loop_error):
        super().__init__()
        self.loop_error = loop_error
        logging.warning('Template loop error!')

    def __str__(self):
        return 'Invalid inheritance {0}'.format(self.loop_error)
