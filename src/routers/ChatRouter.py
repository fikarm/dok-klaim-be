import os
from pathlib import Path
from uuid import uuid4, UUID
from typing import Any, Annotated, List
from schema import UserInput, ChatMeta, PdfUnggah
from fastapi import APIRouter, Form, File, UploadFile
from datetime import datetime
from core.settings import settings
from src.agents import AgentGraph, get_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, AnyMessage

ChatRouter = APIRouter()


async def _handle_input(
    user_input: UserInput, agent: AgentGraph
) -> tuple[dict[str, Any], UUID]:
    """
    Parse user input and handle any required interrupt resumption.
    Returns kwargs for agent invocation and the run_id.
    """
    run_id = uuid4()
    thread_id = user_input.thread_id or str(uuid4())
    user_id = user_input.user_id or str(uuid4())
    configurable = {"thread_id": thread_id, "user_id": user_id}
    config = RunnableConfig(configurable=configurable, run_id=run_id)
    input = {"messages": [HumanMessage(content=user_input.message)]}
    kwargs = {"input": input, "config": config}
    return kwargs, run_id


def uploaded_files_as_system_message(messages: list[AnyMessage]):
    """Jika ada file yang diupload oleh user, maka buat system message yang berisi list file tersebut."""
    # TODO


@ChatRouter.get("/cobi")
async def cobi():
    # return UserInput(message="msg", user_id="1", thread_id="1").model_dump()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"sekarang jam {current_time}"


@ChatRouter.post("/{agent_name}/invoke")
async def agent_invoke(
    agent_name: str,
    thread_id: Annotated[str, Form()],
    message: Annotated[str, Form()],
    files: list[UploadFile] | None = None,
):
    config = RunnableConfig(configurable={"thread_id": thread_id})
    agent: AgentGraph = get_agent(agent_name)

    # jika user upload files, maka simpan di graph state
    if files:
        fnames = []
        for file in files:
            path = Path(settings.TEMP_DIR, thread_id, file.filename or f"{uuid4()}.pdf")
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(await file.read())
                fnames.append(path)

        agent.update_state(config, {"files": fnames})

    response = agent.invoke(
        {"messages": [HumanMessage(content=message)]}, config=config
    )
    # return "aman"
    return response["messages"][-1].content


# TODO: simpan per sesi
def upload_files(uploadedFiles: list[UploadFile]):
    for uploaded in uploadedFiles:
        upload_path = os.path.join(settings.TEMP_DIR, uploaded.filename or "")

        # upload to temp
        with open(upload_path, "wb") as tmp:
            tmp.write(uploaded.file.read())


# @ChatRouter.post("/invoke")
# async def invoke(user_input: Annotated[UserInput, Form()]):
#     # if user_input.pdfs:
#     #     return user_input.pdfs
#     # user_input

#     messages: List[AnyMessage] = []

#     # jika ada file konversi ke system chat dan beri metadata
#     if user_input.pdfs:
#         upload_files(user_input.pdfs)

#         meta: ChatMeta = ChatMeta(
#             pdfs=[
#                 PdfUnggah(
#                     path=os.path.join(settings.TEMP_DIR, pdf.filename or ""),
#                     name=pdf.filename or "",
#                 )
#                 for pdf in user_input.pdfs
#             ],
#             is_display=False,
#         )

#         if "pdfs" in meta:
#             filenames = "\n".join(
#                 [f"{i + 1}. {pdf.name}" for i, pdf in enumerate(meta["pdfs"])]
#             )

#             system_message = SystemMessage(
#                 content=f"User mengunggah file-file berikut: \n{filenames}\nJangan pernah sebutkan lokasi file-file di atas.",
#                 additional_kwargs=meta,
#             )

#             messages.append(system_message)

#     # human_message = HumanMessage("Halo")
#     # messages.append(human_message)
#     # ai_message = AIMessage("Halo juga")
#     # messages.append(ai_message)

#     human_message = HumanMessage(user_input.message)

#     messages.append(human_message)

#     # call agent
#     # file uploaded
#     # agent: AgentGraph = get_agent(agent_id)
#     # kwargs, run_id = await _handle_input(user_input, agent)

#     response = await agent.agent_dokklaim.ainvoke(
#         {"messages": messages}, stream_mode="values"
#     )

#     return response["messages"]
#     # return response["messages"][-1]
#     # return messages
#     # return os.getcwd()
