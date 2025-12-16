import sys
import types

# Stub langgraph modules
langgraph_pkg = types.ModuleType("langgraph")
sys.modules.setdefault("langgraph", langgraph_pkg)

graph_mod = types.ModuleType("langgraph.graph")
graph_mod.END = "END"

def add_messages(existing, new):
    return (existing or []) + (new or [])

graph_mod.add_messages = add_messages
sys.modules["langgraph.graph"] = graph_mod


types_mod = types.ModuleType("langgraph.types")


class Command:
    def __init__(self, *, update=None, goto=None):
        self.update = update or {}
        self.goto = goto


def interrupt(payload):
    raise RuntimeError("interrupt")


types_mod.Command = Command
types_mod.interrupt = interrupt
sys.modules["langgraph.types"] = types_mod

# Stub langchain_core modules
langchain_core_pkg = types.ModuleType("langchain_core")
sys.modules.setdefault("langchain_core", langchain_core_pkg)

messages_mod = types.ModuleType("langchain_core.messages")


class HumanMessage:
    def __init__(self, content=""):
        self.content = content


AnyMessage = HumanMessage
messages_mod.HumanMessage = HumanMessage
messages_mod.AnyMessage = AnyMessage
sys.modules["langchain_core.messages"] = messages_mod

runnables_mod = types.ModuleType("langchain_core.runnables")


class Runnable:
    def invoke(self, input):
        raise NotImplementedError


runnables_mod.Runnable = Runnable
sys.modules["langchain_core.runnables"] = runnables_mod

# Stub pydantic
pydantic_mod = types.ModuleType("pydantic")


def Field(default=None, *args, **kwargs):
    return default


class BaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def model_validate(cls, data):
        if isinstance(data, cls):
            return data
        return cls(**data)

    def model_dump(self):
        return self.__dict__


pydantic_mod.Field = Field
pydantic_mod.BaseModel = BaseModel
sys.modules["pydantic"] = pydantic_mod

# Stub structlog
structlog_mod = types.ModuleType("structlog")


def _noop_logger(*args, **kwargs):
    class _Logger:
        def info(self, *args, **kwargs):
            pass

    return _Logger()


structlog_mod.get_logger = _noop_logger
sys.modules["structlog"] = structlog_mod

# Expand structlog stub
structlog_mod.configure = lambda *args, **kwargs: None
structlog_mod.getLogger = _noop_logger

# Stub docling_ibm_models hierarchy
base_model_mod = types.ModuleType("docling_ibm_models.tableformer.models.common.base_model")
base_model_mod.LOG_LEVEL = 0
sys.modules["docling_ibm_models.tableformer.models.common.base_model"] = base_model_mod

models_common_mod = types.ModuleType("docling_ibm_models.tableformer.models.common")
models_common_mod.base_model = base_model_mod
sys.modules["docling_ibm_models.tableformer.models.common"] = models_common_mod

models_mod = types.ModuleType("docling_ibm_models.tableformer.models")
models_mod.common = models_common_mod
sys.modules["docling_ibm_models.tableformer.models"] = models_mod

package_mod = types.ModuleType("docling_ibm_models.tableformer")
package_mod.models = models_mod
sys.modules["docling_ibm_models.tableformer"] = package_mod

root_pkg = types.ModuleType("docling_ibm_models")
root_pkg.tableformer = package_mod
sys.modules["docling_ibm_models"] = root_pkg

# Expand langchain_core stubs
langchain_core_pkg.__path__ = []
prompts_mod = types.ModuleType("langchain_core.prompts")


def ChatPromptTemplate(*args, **kwargs):
    class _Prompt:
        def format(self, **kwargs):
            return ""

    return _Prompt()


prompts_mod.ChatPromptTemplate = ChatPromptTemplate
sys.modules["langchain_core.prompts"] = prompts_mod

# Extend structlog stdlib
structlog_mod.stdlib = types.SimpleNamespace(add_log_level=lambda *args, **kwargs: None)

# Rebuild structlog.stdlib with needed attributes

class _BoundLogger:
    def bind(self, **kwargs):
        return self

    def info(self, *args, **kwargs):
        pass


class _LoggerFactory:
    def __call__(self, *args, **kwargs):
        return _BoundLogger()


def _noop_processor(*args, **kwargs):
    return None


structlog_mod.stdlib = types.SimpleNamespace(
    add_log_level=lambda *args, **kwargs: None,
    add_logger_name=lambda *args, **kwargs: None,
    BoundLogger=_BoundLogger,
    LoggerFactory=_LoggerFactory,
)
structlog_mod.processors = types.SimpleNamespace(
    TimeStamper=lambda *args, **kwargs: _noop_processor,
    StackInfoRenderer=lambda *args, **kwargs: _noop_processor,
    dict_tracebacks=lambda *args, **kwargs: None,
    JSONRenderer=lambda *args, **kwargs: _noop_processor,
)
structlog_mod.get_logger = lambda *args, **kwargs: _BoundLogger()

# Stub yaml
yaml_mod = types.ModuleType("yaml")
yaml_mod.safe_load = lambda stream: {}
sys.modules["yaml"] = yaml_mod

# Extend langchain_core.messages
class BaseMessage:
    def __init__(self, content=""):
        self.content = content


messages_mod.BaseMessage = BaseMessage
messages_mod.HumanMessage = HumanMessage
messages_mod.AnyMessage = AnyMessage
sys.modules["langchain_core.messages"] = messages_mod

messages_mod.__path__ = []
utils_mod = types.ModuleType("langchain_core.messages.utils")
utils_mod.get_buffer_string = lambda messages, human_prefix="Human", ai_prefix="AI": ""
sys.modules["langchain_core.messages.utils"] = utils_mod
