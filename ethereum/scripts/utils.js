require("dotenv").config();

const base = process.env.API_BASE || "http://localhost:8080/";

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function post(endpoint, data) {
  const res = await fetch(base + endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return await res.json();
}

async function get(endpoint) {
  const res = await fetch(base + endpoint, { method: "GET" });
  return await res.json();
}

module.exports = {
  sleep,
  post,
  get,
};
