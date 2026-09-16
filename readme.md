# 🛡️ SafeSathi – AI Digital Safety Assistant

SafeSathi is an AI-powered digital safety assistant designed to help users, especially senior citizens, identify potentially fraudulent messages, calls, links, and screenshots.

The system combines Machine Learning, Natural Language Processing (NLP), OCR, speech-to-text, URL analysis, and rule-based scam detection to provide a simple and understandable risk assessment.

---

## 🚨 Problem Statement

Online scams are becoming increasingly common through:

- Fraudulent SMS and WhatsApp messages
- Fake banking and KYC requests
- Phishing links
- Lottery and prize scams
- Fake courier messages
- Technical-support scams
- Impersonation and fake authority calls
- Fake family emergency messages

Senior citizens and users with limited digital awareness may find it difficult to determine whether a message, call, or link is genuine.

SafeSathi aims to provide a simple interface where users can submit suspicious content and receive an easy-to-understand safety assessment.

---

## 💡 Solution

SafeSathi allows users to analyze suspicious content using multiple input methods:

### 📱 1. Text / Message Analysis
Users can paste suspicious SMS, WhatsApp messages, emails, or other text.

The system analyzes:

- Scam-related keywords
- Urgency patterns
- Financial requests
- OTP/PIN requests
- KYC-related language
- Threatening language
- Prize/lottery claims
- Suspicious URLs

---

### 🎤 2. Voice Input

Users can provide a voice recording or speech input.

The system converts:

**Voice → Speech-to-Text → Text Analysis → Scam Detection**

This makes the application easier to use for elderly users.

---

### 📸 3. Screenshot Analysis

Users can upload a screenshot of a suspicious message.

SafeSathi uses OCR (Optical Character Recognition) to extract text from the image.

The process is:

**Screenshot → OCR → Extracted Text → Scam Detection**

This is useful for analyzing:

- WhatsApp screenshots
- SMS screenshots
- Banking messages
- Fake KYC messages
- Suspicious payment requests

---

## 🔗 URL Risk Analysis

If a message contains a URL, SafeSathi extracts and analyzes the link.

The system checks for suspicious characteristics such as:

- Suspicious URL keywords
- Unusual domains
- Phishing-related patterns
- Urgency-related link messages
- Potentially dangerous URL structures

The URL analysis is combined with the message analysis to provide additional risk information.

---

## 🧠 Machine Learning

SafeSathi uses a Machine Learning-based text classification system.

### Text Processing

The input text is processed using:

- Text cleaning
- Tokenization
- Feature extraction
- TF-IDF vectorization

### Classification

The trained classifier predicts whether the input is potentially:

- Safe
- Suspicious
- Likely Scam

The trained model is stored as:

```text
model/model.pkl