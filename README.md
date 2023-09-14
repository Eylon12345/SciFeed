# SciFeed
New articles summary feed with AI.
An application that fetches, summarizes, and displays scientific articles from Arxiv related to a chosen subject.

![image](https://github.com/Eylon12345/SciFeed/assets/121553761/28356931-68ce-4963-898e-f74b68e89b0c)

### Setting Up loacaly:
1. Clone the repository.
2. Set your OpenAI API key:

   For Mac/Linux:
   ```bash
   export OPENAI_API_KEY='your_api_key'
   ```

   For Windows (Command Prompt):
   ```bash
   set OPENAI_API_KEY=your_api_key
   ```

   For Windows (PowerShell):
   ```bash
   $env:OPENAI_API_KEY='your_api_key'
   ```

3. Run the application:
```bash
streamlit run app.py
```
Navigate to the provided local URL in your browser.

### Features:
- Search for articles using specific keywords.
- Display articles in both expanded and card views.
- Automatic summarization of articles using OpenAI's GPT model.
- (Optional) Periodic fetching of articles.

---

Note: Ensure that the main application file is named `app.py` when using the above command.
