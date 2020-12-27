import bleach
from sqlalchemy import TypeDecorator, Text
from flask import current_app


class CleanedHtml(TypeDecorator):
    """
    Cleans HTML on the way out of the database.     
    """

    # Add the additional html cleaning functionality to the Text type.
    impl = Text

    def process_result_value(self, value, dialect):
        """ 
        Fires the self._clean_html method on the way out of the database 
        and returns 'clean' html 
        """
        return self._clean_html(value)

    def _clean_html(self, html):
        """ 
        Cleans user HTML input.
        Returns: Cleaned html.
        """
        return bleach.clean(html,
                            tags=current_app.config['HTML_CLEAN_ALLOWED_TAGS'],
                            attributes=current_app.config['HTML_CLEAN_ALLOWED_ATTRS'],
                            styles=current_app.config['HTML_CLEAN_ALLOWED_STYLES'])
