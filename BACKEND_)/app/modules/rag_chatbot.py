"""
RAG-based chatbot module for generating responses based on retrieved context.
"""
import os
import openai
from dotenv import load_dotenv
from app.modules.rule_matcher import RuleMatcher
from langdetect import detect, LangDetectException

class RagChatbot:
    """
    Class for implementing a Retrieval-Augmented Generation (RAG) chatbot.
    """
    
    def __init__(self, vector_retriever, api_key=None, model="gpt-3.5-turbo"):
        """
        Initialize the RAG chatbot with a vector retriever and OpenAI settings.
        
        Args:
            vector_retriever: Vector retriever for retrieving relevant chunks
            api_key (str, optional): OpenAI API key. If None, attempts to load from env
            model (str): OpenAI model to use
        """
        self.vector_retriever = vector_retriever
        self.fallback_matcher = RuleMatcher()
        
        # Try to get API key from environment if not provided
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            
        self.api_key = api_key
        self.model = model
        self.user_language = 'en'  # Default language
        self._context_cache = {}  # Cache for previous contexts
        
        # Greeting templates in different languages
        self.greeting_templates = {
            'en': "Hello! I'm your helpful assistant for company rules and policies. How can I help you today?",
            'es': "¡Hola! Soy su asistente para las reglas y políticas de la empresa. ¿Cómo puedo ayudarle hoy?",
            'fr': "Bonjour! Je suis votre assistant pour les règles et politiques de l'entreprise. Comment puis-je vous aider aujourd'hui?",
            'de': "Hallo! Ich bin Ihr Assistent für Unternehmensregeln und -richtlinien. Wie kann ich Ihnen heute helfen?",
            'it': "Ciao! Sono il tuo assistente per le regole e le politiche aziendali. Come posso aiutarti oggi?",
            'pt': "Olá! Sou seu assistente para regras e políticas da empresa. Como posso ajudá-lo hoje?",
            'zh': "你好！我是您的公司规则和政策助手。今天我能为您做些什么？",
            'ja': "こんにちは！私は会社の規則とポリシーについてのアシスタントです。今日はどのようにお手伝いできますか？",
            'hi': "नमस्ते! मैं कंपनी के नियमों और नीतियों के लिए आपका सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
            'ru': "Здравствуйте! Я ваш помощник по правилам и политикам компании. Чем я могу помочь вам сегодня?",
            'gu': "નમસ્તે! હું કંપનીના નિયમો અને નીતિઓ માટે તમારો સહાયક છું. આજે હું તમારી કેવી રીતે મદદ કરી શકું?"
        }
        
        # Not found templates in different languages
        self.not_found_templates = {
            'en': "I couldn't find any relevant rules or policies that address your question.",
            'es': "No pude encontrar reglas o políticas relevantes que respondan a su pregunta.",
            'fr': "Je n'ai pas trouvé de règles ou de politiques pertinentes qui répondent à votre question.",
            'de': "Ich konnte keine relevanten Regeln oder Richtlinien finden, die Ihre Frage beantworten.",
            'it': "Non ho trovato regole o politiche rilevanti che rispondano alla tua domanda.",
            'pt': "Não consegui encontrar regras ou políticas relevantes que respondam à sua pergunta.",
            'zh': "我找不到解决您问题的相关规则或政策。",
            'ja': "あなたの質問に対応する関連規則やポリシーを見つけることができませんでした。",
            'hi': "मुझे आपके प्रश्न का समाधान करने वाले कोई प्रासंगिक नियम या नीतियां नहीं मिलीं।",
            'ru': "Я не смог найти соответствующих правил или политик, которые отвечают на ваш вопрос.",
            'gu': "મને તમારા પ્રશ્નનો જવાબ આપતા કોઈપણ સંબંધિત નિયમો અથવા નીતિઓ મળી નથી."
        }
        
        # Found info templates in different languages
        self.found_info_templates = {
            'en': "Here's what I found in our policies: {}",
            'es': "Esto es lo que encontré en nuestras políticas: {}",
            'fr': "Voici ce que j'ai trouvé dans nos politiques: {}",
            'de': "Hier ist, was ich in unseren Richtlinien gefunden habe: {}",
            'it': "Ecco cosa ho trovato nelle nostre politiche: {}",
            'pt': "Aqui está o que encontrei em nossas políticas: {}",
            'zh': "这是我在我们的政策中找到的内容：{}",
            'ja': "ポリシーで見つけた内容は次のとおりです：{}",
            'hi': "हमारी नीतियों में मुझे यह मिला: {}",
            'ru': "Вот что я нашел в наших правилах: {}",
            'gu': "અમારી નીતિઓમાં મને આ મળ્યું: {}"
        }
        
        # No need to set global API key in newer OpenAI SDK version
        
    def detect_language(self, text):
        """
        Detect the language of the given text.
        
        Args:
            text (str): Text to detect language for
            
        Returns:
            str: Language code (e.g., 'en', 'es', 'fr')
        """
        # Only detect if the text is long enough
        if len(text.strip()) < 5:
            return self.user_language  # Return last used language for very short queries
        
        # Handle common language-specific greetings directly
        greeting_language_map = {
            'hello': 'en', 'hi': 'en', 'hey': 'en',
            'hola': 'es', 'buenos días': 'es',
            'bonjour': 'fr', 'salut': 'fr',
            'hallo': 'de', 'guten tag': 'de',
            'ciao': 'it', 'salve': 'it',
            'olá': 'pt', 'oi': 'pt',
            '你好': 'zh', '您好': 'zh',
            'こんにちは': 'ja', 'はい': 'ja',
            'नमस्ते': 'hi', 'नमस्कार': 'hi',
            'привет': 'ru', 'здравствуйте': 'ru',
            'નમસ્તે': 'gu', 'જય શ્રી કૃષ્ણ': 'gu'
        }
        
        text_lower = text.lower().strip()
        
        # Check if query starts with a known greeting
        for greeting, lang in greeting_language_map.items():
            if text_lower.startswith(greeting):
                print(f"Language detected from greeting: {lang}")
                self.user_language = lang  # Update stored language preference
                return lang
        
        try:
            # Configure langdetect for more stable results
            from langdetect import DetectorFactory
            DetectorFactory.seed = 0  # Make detection deterministic
            
            detected_lang = detect(text)
            print(f"Language detected: {detected_lang}")
            
            # Validate detected language (make sure it's one we support)
            supported_languages = set(self.greeting_templates.keys())
            if detected_lang not in supported_languages:
                # Default to English if detected language is not supported
                print(f"Detected language {detected_lang} not supported, defaulting to English")
                detected_lang = 'en'
            
            self.user_language = detected_lang  # Update stored language preference
            return detected_lang
        except LangDetectException as e:
            print(f"Language detection failed: {e}")
            return self.user_language  # Use last detected language if detection fails
    
    def get_template(self, template_dict, lang_code):
        """
        Get the appropriate template for a given language.
        
        Args:
            template_dict (dict): Dictionary of templates by language
            lang_code (str): Language code
            
        Returns:
            str: Template in the requested language or English as fallback
        """
        return template_dict.get(lang_code, template_dict['en'])
        
    def load_rules_for_fallback(self, rules_dict):
        """
        Load rules for fallback keyword-based matching.
        
        Args:
            rules_dict (dict): Dictionary of rules with rule_id as keys
        """
        self.fallback_matcher.load_rules_from_dict(rules_dict)
    
    def answer_query(self, query, top_k=3, use_fallback=True):
        """
        Generate a response for a user query using RAG.
        
        Args:
            query (str): User query
            top_k (int): Number of chunks to retrieve
            use_fallback (bool): Whether to use fallback matching if RAG is unavailable
            
        Returns:
            dict: Response containing answer and metadata
        """
        # Detect language
        lang_code = self.detect_language(query)
        print(f"Query language detected as: {lang_code}")  # Debug info
        
        # Check for greetings and return fixed responses
        query_lower = query.lower().strip()
        
        # Greetings in multiple languages
        greetings = {
            'en': ["hi", "hello", "hey", "hii", "hiii", "greetings"],
            'es': ["hola", "saludos"],
            'fr': ["bonjour", "salut"],
            'de': ["hallo", "guten tag"],
            'it': ["ciao", "salve"],
            'pt': ["oi", "olá"],
            'zh': ["你好", "您好"],
            'ja': ["こんにちは", "やあ"],
            'hi': ["नमस्ते", "हैलो"],
            'ru': ["привет", "здравствуйте"]
        }
        
        # Check if query is a greeting in any language
        is_greeting = False
        for lang, greeting_list in greetings.items():
            if any(greeting == query_lower for greeting in greeting_list):
                is_greeting = True
                lang_code = lang  # Set language based on greeting
                self.user_language = lang  # Update stored language preference
                print(f"Greeting detected in language: {lang_code}")
                break
        
        if is_greeting:
            greeting_template = self.get_template(self.greeting_templates, lang_code)
            return {
                "answer": greeting_template,
                "chunks": [],
                "method": "fixed_greeting",
                "language": lang_code
            }
            
        # Store the language code for consistent use throughout this query response
        response_language = lang_code
        
        # Check if vector retriever and OpenAI are available
        retrieval_available = (self.vector_retriever and 
                              self.vector_retriever.is_available() and 
                              self.vector_retriever.index is not None)
        
        generation_available = self.api_key is not None
        
        # If both retrieval and generation are available, use RAG
        if retrieval_available and generation_available:
            return self._answer_with_rag(query, top_k, response_language)
        
        # If vector retriever is available but not OpenAI, use retrieval only
        elif retrieval_available and not generation_available:
            return self._answer_with_retrieval_only(query, top_k, response_language)
            
        # Use fallback keyword-based matching if available and requested
        elif use_fallback:
            return self._answer_with_fallback(query, response_language)
            
        # No method available to answer the query
        else:
            return {
                "answer": self.get_template(self.not_found_templates, response_language),
                "chunks": [],
                "method": "none",
                "language": response_language
            }
            
    def _answer_with_rag(self, query, top_k=3, lang_code='en'):
        """
        Generate a response using RAG (retrieval + generation).
        
        Args:
            query (str): User query
            top_k (int): Number of chunks to retrieve
            lang_code (str): Language code for the response
            
        Returns:
            dict: Response containing answer and metadata
        """
        # Retrieve relevant chunks
        relevant_chunks = self.vector_retriever.retrieve(query, top_k)
        
        if not relevant_chunks:
            return {
                "answer": self.get_template(self.not_found_templates, lang_code),
                "chunks": [],
                "method": "rag_no_chunks",
                "language": lang_code
            }
            
        # Validate retrieved chunks
        # Check if the chunks are truly relevant by looking for keyword matches
        query_keywords = [word.lower() for word in query.split() if len(word) > 3]
        has_relevant_match = False
        
        if query_keywords:
            for chunk in relevant_chunks:
                chunk_lower = chunk.lower()
                if any(keyword in chunk_lower for keyword in query_keywords):
                    has_relevant_match = True
                    break
                    
            if not has_relevant_match and lang_code != 'en':  # Apply stricter validation for non-English
                return {
                    "answer": self.get_template(self.not_found_templates, lang_code),
                    "chunks": [],
                    "method": "rag_no_relevant_match",
                    "language": lang_code
                }
            
        # Generate a response using OpenAI
        try:
            # Process chunks to extract the most relevant information
            processed_chunks = []
            query_keywords = [word.lower() for word in query.split() if len(word) > 2]
            
            for chunk in relevant_chunks:
                # Split into sentences and score them
                sentences = [s.strip() for s in chunk.split('.') if s.strip()]
                scored_sentences = []
                
                for sentence in sentences:
                    # Score based on keyword matches and sentence length
                    sentence_lower = sentence.lower()
                    keyword_score = sum(1 for keyword in query_keywords if keyword in sentence_lower)
                    length_score = min(len(sentence.split()) / 20, 1)  # Normalize by reasonable sentence length
                    total_score = keyword_score + length_score
                    
                    if total_score > 0:
                        scored_sentences.append((total_score, sentence))
                
                # Add the best sentences from this chunk
                if scored_sentences:
                    scored_sentences.sort(reverse=True)
                    processed_chunks.extend([s[1] for s in scored_sentences[:2]])
            
            # If we found relevant sentences, use them; otherwise use the original chunks
            context = "\n\n".join(processed_chunks if processed_chunks else relevant_chunks)
            
            # Multilingual system prompt based on detected language
            system_prompts = {
                'en': "You are a helpful assistant that answers questions about company rules and policies. Provide clear, concise answers based on the context. If the context contains relevant information, use it to answer the question. If the context doesn't contain enough information, say so in a helpful way.",
                'es': "Eres un asistente útil que responde preguntas sobre las reglas y políticas de la empresa. Proporciona respuestas claras y concisas basadas en el contexto. Si el contexto contiene información relevante, úsala para responder la pregunta. Si el contexto no contiene suficiente información, indícalo de manera útil.",
                'fr': "Vous êtes un assistant utile qui répond aux questions sur les règles et les politiques de l'entreprise. Fournissez des réponses claires et concises basées sur le contexte. Si le contexte contient des informations pertinentes, utilisez-les pour répondre à la question. Si le contexte ne contient pas assez d'informations, indiquez-le de manière utile.",
                'de': "Sie sind ein hilfreicher Assistent, der Fragen zu Unternehmensregeln und -richtlinien beantwortet. Geben Sie klare, prägnante Antworten basierend auf dem Kontext. Wenn der Kontext relevante Informationen enthält, verwenden Sie diese zur Beantwortung der Frage. Wenn der Kontext nicht genügend Informationen enthält, teilen Sie dies hilfreich mit.",
                'it': "Sei un assistente utile che risponde a domande sulle regole e le politiche aziendali. Fornisci risposte chiare e concise basate sul contesto. Se il contesto contiene informazioni rilevanti, usale per rispondere alla domanda. Se il contesto non contiene informazioni sufficienti, indicarlo in modo utile.",
                'pt': "Você é um assistente útil que responde a perguntas sobre regras e políticas da empresa. Forneça respostas claras e concisas baseadas no contexto. Se o contexto contiver informações relevantes, use-as para responder à pergunta. Se o contexto não contiver informações suficientes, indique isso de forma útil.",
                'zh': "您是一位有用的助手，可以回答有关公司规则和政策的问题。根据上下文提供清晰、简洁的答案。如果上下文包含相关信息，请使用它来回答问题。如果上下文没有足够的信息，请以有帮助的方式说明。",
                'ja': "あなたは会社の規則とポリシーに関する質問に答える役立つアシスタントです。文脈に基づいて明確で簡潔な回答を提供してください。文脈に関連する情報が含まれている場合は、それを使用して質問に答えてください。文脈に十分な情報が含まれていない場合は、役立つ方法でその旨を伝えてください。",
                'hi': "आप एक सहायक सहायक हैं जो कंपनी के नियमों और नीतियों के बारे में प्रश्नों का उत्तर देते हैं। संदर्भ के आधार पर स्पष्ट, संक्षिप्त उत्तर प्रदान करें। यदि संदर्भ में प्रासंगिक जानकारी है, तो उसका उपयोग प्रश्न का उत्तर देने के लिए करें। यदि संदर्भ में पर्याप्त जानकारी नहीं है, तो इसे सहायक तरीके से बताएं।",
                'ru': "Вы - полезный помощник, который отвечает на вопросы о правилах и политиках компании. Предоставляйте четкие, лаконичные ответы на основе контекста. Если контекст содержит релевантную информацию, используйте её для ответа на вопрос. Если в контексте недостаточно информации, сообщите об этом полезным способом.",
                'gu': "તમે કંપનીના નિયમો અને નીતિઓ વિશેના પ્રશ્નોનો જવાબ આપતા ઉપયોગી સહાયક છો. સંદર્ભના આધારે સ્પષ્ટ, સંક્ષિપ્ત જવાબો આપો. જો સંદર્ભમાં સંબંધિત માહિતી હોય, તેનો ઉપયોગ પ્રશ્નનો જવાબ આપવા માટે કરો. જો સંદર્ભમાં પૂરતી માહિતી ન હોય, તેને ઉપયોગી રીતે જણાવો."
            }
            
            # Language instruction based on detected language
            language_instructions = {
                'en': "IMPORTANT: Your response MUST be in English.",
                'es': "IMPORTANTE: Tu respuesta DEBE ser en español.",
                'fr': "IMPORTANT: Votre réponse DOIT être en français.",
                'de': "WICHTIG: Ihre Antwort MUSS auf Deutsch sein.",
                'it': "IMPORTANTE: La tua risposta DEVE essere in italiano.",
                'pt': "IMPORTANTE: Sua resposta DEVE ser em português.",
                'zh': "重要提示：您的回答必须是中文。",
                'ja': "重要：あなたの回答は日本語でなければなりません。",
                'hi': "महत्वपूर्ण: आपका उत्तर हिंदी में होना चाहिए।",
                'ru': "ВАЖНО: Ваш ответ ДОЛЖЕН быть на русском языке.",
                'gu': "મહત્વપૂર્ણ: તમારો જવાબ ગુજરાતીમાં હોવો જોઈએ."
            }
            
            system_prompt = system_prompts.get(lang_code, system_prompts['en'])
            language_instruction = language_instructions.get(lang_code, language_instructions['en'])
            
            prompt = f"""
{system_prompt}

Context:
{context}

Question: {query}

{language_instruction}
"""
            
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\n" + language_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "answer": answer,
                "chunks": relevant_chunks,
                "method": "rag",
                "language": lang_code
            }
            
        except Exception as e:
            print(f"Error generating response with OpenAI: {e}")
            error_messages = {
                'en': f"I found relevant information but encountered an error generating a response: {str(e)}",
                'es': f"Encontré información relevante pero ocurrió un error al generar una respuesta: {str(e)}",
                'fr': f"J'ai trouvé des informations pertinentes mais j'ai rencontré une erreur lors de la génération d'une réponse: {str(e)}",
                'de': f"Ich habe relevante Informationen gefunden, aber bei der Generierung einer Antwort ist ein Fehler aufgetreten: {str(e)}",
                'it': f"Ho trovato informazioni rilevanti ma ho riscontrato un errore durante la generazione di una risposta: {str(e)}",
                'pt': f"Encontrei informações relevantes, mas encontrei um erro ao gerar uma resposta: {str(e)}",
                'zh': f"我找到了相关信息，但在生成响应时遇到错误：{str(e)}",
                'ja': f"関連情報を見つけましたが、応答の生成中にエラーが発生しました：{str(e)}",
                'hi': f"मुझे प्रासंगिक जानकारी मिली लेकिन एक प्रतिक्रिया उत्पन्न करते समय एक त्रुटि का सामना करना पड़ा: {str(e)}",
                'ru': f"Я нашел актуальную информацию, но при создании ответа возникла ошибка: {str(e)}",
                'gu': f"તમારો જવાબ ગુજરાતીમાં હોવો જોઈએ તેનો ઉપયોગ પ્રશ્નનો જવાબ આપવા માટે કરો જો સંદર્ભમાં પૂરતી માહિતી ન હોય, તેને ઉપયોગી રીતે જણાવો."
            }
            
            error_message = error_messages.get(lang_code, error_messages['en'])
            
            return {
                "answer": error_message,
                "chunks": relevant_chunks,
                "method": "rag_error",
                "language": lang_code
            }
        
    def _answer_with_retrieval_only(self, query, top_k=3, lang_code='en'):
        """
        Generate a response using retrieval only (no generation).
        
        Args:
            query (str): User query
            top_k (int): Number of chunks to retrieve
            lang_code (str): Language code for the response
            
        Returns:
            dict: Response containing answer and metadata
        """
        # Retrieve relevant chunks
        relevant_chunks = self.vector_retriever.retrieve(query, top_k)
        
        if not relevant_chunks:
            return {
                "answer": self.get_template(self.not_found_templates, lang_code),
                "chunks": [],
                "method": "retrieval_no_chunks",
                "language": lang_code
            }
        
        # Validate retrieved chunks
        # Check if the chunks are truly relevant by looking for keyword matches
        query_keywords = [word.lower() for word in query.split() if len(word) > 3]
        has_relevant_match = False
        
        if query_keywords:
            for chunk in relevant_chunks:
                chunk_lower = chunk.lower()
                if any(keyword in chunk_lower for keyword in query_keywords):
                    has_relevant_match = True
                    break
                    
            if not has_relevant_match:
                return {
                    "answer": self.get_template(self.not_found_templates, lang_code),
                    "chunks": [],
                    "method": "retrieval_no_relevant_match",
                    "language": lang_code
                }
        
        # Process the chunks to provide more focused answers
        query_keywords = [word.lower() for word in query.split() if len(word) > 3]
        
        # Try to extract the most relevant sentences from chunks
        all_sentences = []
        
        for chunk in relevant_chunks:
            # Split into sentences and clean them
            chunk_sentences = [s.strip() for s in chunk.split('.') if s.strip()]
            
            # Score sentences by the number of query keywords they contain
            scored_sentences = []
            for sentence in chunk_sentences:
                sentence_lower = sentence.lower()
                score = sum(1 for keyword in query_keywords if keyword in sentence_lower)
                if score > 0:
                    scored_sentences.append((score, sentence))
            
            # Add the top sentences from this chunk
            if scored_sentences:
                scored_sentences.sort(reverse=True)
                all_sentences.extend([s[1] for s in scored_sentences[:2]])
        
        template = self.get_template(self.found_info_templates, lang_code)
        
        if all_sentences:
            # Use the most relevant sentences (max 3)
            concise_answer = '. '.join(all_sentences[:3]) + '.'
            return {
                "answer": template.format(concise_answer),
                "chunks": relevant_chunks,
                "method": "retrieval_only",
                "language": lang_code
            }
        else:
            # If we couldn't extract relevant sentences, use the most relevant chunk
            # but limit to a reasonable length
            first_chunk = relevant_chunks[0]
            if len(first_chunk) > 300:
                # Find a reasonable breakpoint (end of sentence near 300 chars)
                breakpoint = first_chunk.rfind('.', 0, 300)
                if breakpoint > 0:
                    first_chunk = first_chunk[:breakpoint+1]
            
            return {
                "answer": template.format(first_chunk),
                "chunks": relevant_chunks,
                "method": "retrieval_only",
                "language": lang_code
            }
        
    def _answer_with_fallback(self, query, lang_code='en'):
        """
        Generate a response using keyword-based fallback matching.
        
        Args:
            query (str): User query
            lang_code (str): Language code for the response
            
        Returns:
            dict: Response containing answer and metadata
        """
        # Find matching rules using keyword matching
        matched_rules = self.fallback_matcher.match_by_keywords(query)
        
        if not matched_rules:
            return {
                "answer": self.get_template(self.not_found_templates, lang_code),
                "chunks": [],
                "method": "fallback_no_match",
                "language": lang_code
            }
        
        # For non-English queries, apply stricter validation to prevent false positives
        if lang_code != 'en':
            # Check if the matched rules actually contain information related to the query
            query_keywords = [word.lower() for word in query.split() if len(word) > 3]
            valid_matches = {}
            
            for rule_id, rule_text in matched_rules.items():
                text_to_check = rule_text
                if isinstance(rule_text, dict):
                    text_to_check = rule_text.get('text', '')
                
                # Only keep matches that actually contain the query keywords
                text_lower = text_to_check.lower()
                if query_keywords and any(keyword in text_lower for keyword in query_keywords):
                    valid_matches[rule_id] = rule_text
            
            # If no valid matches after stricter validation, return not found
            if not valid_matches:
                return {
                    "answer": self.get_template(self.not_found_templates, lang_code),
                    "chunks": [],
                    "method": "fallback_no_valid_match",
                    "language": lang_code
                }
            
            # Use the valid matches instead
            matched_rules = valid_matches
            
        # Use the matched rules as the answer
        rules_text = []
        for rule_id, rule_text in matched_rules.items():
            if isinstance(rule_text, dict):
                rules_text.append(rule_text.get('text', ''))
            else:
                rules_text.append(rule_text)
        
        template = self.get_template(self.found_info_templates, lang_code)
                
        return {
            "answer": template.format(rules_text[0]),
            "chunks": rules_text,
            "method": "fallback",
            "language": lang_code
        }

    def reset_context(self):
        """
        Reset the context of the chatbot.
        """
        self._context_cache = {}
        self.fallback_matcher.reset_rules() 