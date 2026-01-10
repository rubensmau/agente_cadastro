eu preciso de um agente que tem acesso a uma planilha csv com cadastro de pessoas ( nome, sobrenome,endereco, cidade,estado, telefone,cpf ).Através de interface a2a . It should handle image processing and expose an Agent Card on /metadata. Através de configuração  será possivel configurar quais destes dados serão enviados para o cliente. Este será um modelo que servirá de base para diversas instalacoes , assim tem que ser facilmente configuravel. Programa python. Prepare um arquivo csv para testes e o arquivo de configuracao.  


Use framework python-adk


example lib usage
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from .remote_agent_connection import RemoteAgentConnections

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)

from a2a.client import A2AClient
from a2a.types import AgentCapabilities, AgentSkill, AgentCard
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore


