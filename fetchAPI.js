const axios = require('axios');
const fs = require('fs');

const API_KEY = '62a4b058a96d71.91558808';
const API_URL = `https://eodhd.com/api/news?offset=0&limit=10&fmt=json`;

const params = {
    s: 'APPL.US',
	api_token: API_KEY,
};


async function callAPI() {
    console.log("testing");
    try {
        const response = await axios.get(API_URL, {params});
        
        // fs.writeFile('data.json', jsonData, (err) => {
        // });
        
    } catch (error) {
        console.error('Error fetching data:', error.message);
    }   
}

callAPI();

//add cleaing script
/*
(async () => {
	console.log("testing");
    try {
        const res = await axios.get(API_URL);
        console.log(res);
    } catch (error) {
        console.error('Error fetching data:', error.message);
    }   
});
*/