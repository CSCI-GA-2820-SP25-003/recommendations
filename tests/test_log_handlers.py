from service.common import log_handlers
from service import create_app
import logging


def test_init_logging_sets_formatter_and_level():
    """It should initialize the app logger with correct formatter"""
    app = create_app()

    # 添加一个可控的 logger（模拟 gunicorn.error）
    test_logger = logging.getLogger("test.logger")
    stream_handler = logging.StreamHandler()
    test_logger.addHandler(stream_handler)
    test_logger.setLevel(logging.INFO)

    # 初始化日志
    log_handlers.init_logging(app, "test.logger")

    # 断言 app.logger 继承了 handler，并且 formatter 被设置
    for handler in app.logger.handlers:
        assert isinstance(handler.formatter, logging.Formatter)
        formatted = handler.formatter.format(
            logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname=__file__,
                lineno=10,
                msg="message",
                args=(),
                exc_info=None,
            )
        )
        assert "message" in formatted
