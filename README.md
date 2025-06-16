🚀 LLM-Powered Job Description Rewriter API 

A FastAPI-based service that rewrites raw job descriptions into:
Concise
Inclusive
SEO-Optimized versions
using OpenAI's GPT API. It includes authentication, rate limiting, logging to MySQL, and a /metrics endpoint.

📦 Features
  * /rewrite: POST endpoint to rewrite job descriptions (JWT-protected, rate-limited).

  * Prompt engineering layer with OpenAI.

  * Logs to MySQL with latency and tone stats.

  * /metrics: Get API usage and latency insights.

  * JWT-based authentication.

  * Rate limiting with slowapi.

🛠 Installation

  git clone https://github.com/your-username/jd_rewriter.git
  
  cd jd_rewriter
  
  python -m venv venv
  
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  
  pip install -r requirements.txt


⚙️ Environment Setup
*
* Create a .env file:

  OPENAI_API_KEY=your_openai_key

  DATABASE_URL=mysql+mysqlconnector://root:yourpassword@localhost:3306/jdlogs

  SECRET_KEY=your_jwt_secret

▶️ Running the App

  * uvicorn app.main:app --reload

  * Access docs: http://localhost:8000/docs

🔐 Authentication

 * Hit /login with:

  Username: admin
  
  Password: admin123

🛠 Usage

🔐 Login

POST /login

Body (form data):

username=admin

password=admin123

🔁 Rewrite JD

POST /rewrite

Headers: Authorization: Bearer <your_token>

Body (JSON):

{
  "jd_text": "Need a passionate frontend developer",
  
  "tone": "professional"
}

  
📊 Metrics

GET /metrics

Returns:

Total requests

Average latency

Tone usage counts

📌 Notes

Make sure MySQL is running and database jdlogs is created.

Logs are stored in JDRewriteLog table.
