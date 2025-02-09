const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config({ path: './.env' });

const app = express();
app.use(cors());
app.use(express.json());

const GOOGLE_API_KEY = "AIzaSyCEbn8bq8qCFT3nl0_7ft1ub_V-qehNLlQ"; 
const MODEL_NAME = 'gemini-1.5-flash';

app.post('/api/chat', async (req, res) => {
    const { message } = req.body;

    try {
        const response = await axios.post(
            `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${GOOGLE_API_KEY}`,  
            {
                contents: [
                    {
                        role: 'user',
                        parts: [{ text: message }],
                    },
                ],
            },
            {
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        const botResponse = response.data.candidates[0].content.parts[0].text;
        res.json({
            response: botResponse.trim(),
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Something went wrong' });
    }
});

const PORT = 5002;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});