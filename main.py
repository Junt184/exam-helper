import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# 1. 初始化：加载环境变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

if not DEEPSEEK_API_KEY:
    logger.warning("Warning: DEEPSEEK_API_KEY is not set in .env file! 😳")

# 确保保存历史记录的文件夹存在
HISTORY_DIR = "history"
os.makedirs(HISTORY_DIR, exist_ok=True)

app = FastAPI()

# 2. CORS配置 (关键)
# 允许所有来源，确保本地 HTML 文件可以直接访问后端接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法 (GET, POST, etc.)
    allow_headers=["*"],  # 允许所有头信息
)

# 新增：根路径返回 index.html
@app.get("/")
async def read_root():
    return FileResponse('index.html')

# 3. 数据模型
class TextInput(BaseModel):
    text: str

class LoginRequest(BaseModel):
    username: str
    password: str

class QuizCreateRequest(BaseModel):
    name: str
    content: str

# DeepSeek API 配置
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# 加载 System Prompt
PROMPTS_FILE = "prompts.json"
try:
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts_data = json.load(f)
        raw_prompt = prompts_data.get("system_prompt", "")
        if isinstance(raw_prompt, list):
            SYSTEM_PROMPT = "\n".join(raw_prompt)
        else:
            SYSTEM_PROMPT = raw_prompt
            
        if not SYSTEM_PROMPT:
            logger.warning(f"Warning: 'system_prompt' is empty in {PROMPTS_FILE}")
except Exception as e:
    logger.error(f"Error loading prompts.json: {e}")
    SYSTEM_PROMPT = "你是一个助手。" # Fallback

def process_text_with_llm(text: str):
    """
    Helper: 调用 LLM 并清洗数据
    """
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured.")

    # 4. 使用 OpenAI SDK 请求 DeepSeek API
    logger.info("Starting request to DeepSeek API... 🚀")
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        stream=False,
        temperature=0.1
    )
    
    # 保存原始响应 JSON
    result_json = response.model_dump()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{HISTORY_DIR}/response_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    logger.info(f"DeepSeek response saved to {filename} 💾")
    
    # 获取 AI 返回的原始内容
    content = response.choices[0].message.content
    logger.info("Successfully received content from DeepSeek.")
    
    # 5. 数据清洗逻辑
    cleaned_data = []
    
    # 去除可能存在的 Markdown 代码块标记
    content = content.replace("```json", "").replace("```", "").strip()
    
    # 按行分割
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            # 尝试解析每一行 JSON
            parsed_item = json.loads(line)
            
            # 兼容旧格式（数组）和新格式（字典）
            if isinstance(parsed_item, list) and len(parsed_item) >= 3:
                # 旧格式转新格式
                cleaned_data.append({
                    "type": "single",
                    "question": parsed_item[0],
                    "answer": parsed_item[1],
                    "options": parsed_item[2]
                })
            elif isinstance(parsed_item, dict):
                # 简单校验必要字段
                if "type" in parsed_item and "question" in parsed_item and "answer" in parsed_item:
                    cleaned_data.append(parsed_item)
                else:
                    logger.warning(f"Skipping dict missing fields: {line}")
            else:
                logger.warning(f"Skipping unknown format: {line}")

        except json.JSONDecodeError:
            logger.warning(f"Skipping invalid JSON line: {line}")
            continue
    
    logger.info(f"Successfully processed {len(cleaned_data)} questions.")
    return cleaned_data

@app.post("/api/login")
def login(request: LoginRequest):
    if request.username == "student" and request.password == "123123":
        return {"status": "success", "token": "fake-jwt-token-123"}
    raise HTTPException(status_code=401, detail="用户名或密码错误 🙅‍♂️")

@app.get("/api/quizzes")
def list_quizzes():
    quizzes = []
    quizzes_dir = "quizzes"
    if not os.path.exists(quizzes_dir):
        return []
    
    # 按修改时间倒序排列
    files = [f for f in os.listdir(quizzes_dir) if f.endswith(".json")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(quizzes_dir, x)), reverse=True)
    
    for filename in files:
        quizzes.append({"id": filename.replace(".json", ""), "name": filename.replace(".json", "")})
    return quizzes

@app.post("/api/quizzes")
def create_quiz(request: QuizCreateRequest):
    try:
        # 1. 调用 LLM 解析题目
        questions = process_text_with_llm(request.content)
        
        if not questions:
             raise HTTPException(status_code=400, detail="未能解析出任何题目，请检查输入格式 🥺")

        # 2. 保存到文件
        filename = f"quizzes/{request.name}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
            
        return {"status": "success", "count": len(questions)}
    except Exception as e:
        logger.error(f"Error creating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quizzes/{name}")
def get_quiz(name: str):
    filepath = f"quizzes/{name}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Quiz not found 🤷‍♂️")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading quiz: {e}")

@app.post("/convert")
def convert_text(input_data: TextInput):
    """
    核心接口：接收文本 -> 调用 DeepSeek -> 清洗数据 -> 返回 JSON 数组
    (保留旧接口以兼容)
    """
    try:
        data = process_text_with_llm(input_data.text)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=8000)
