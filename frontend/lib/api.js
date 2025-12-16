import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("accessToken");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(username, password) {
  return api.post("/auth/login/", { username, password });
}

export async function register(username, email, password) {
  return api.post("/auth/register/", { username, email, password });
}

export async function getFacebookAuthURL() {
  return api.get("/facebook/oauth_url/");
}

export async function fetchPages() {
  return api.get("/facebook/pages/");
}

export async function fetchScheduledPosts() {
  return api.get("/scheduled_posts/");
}

export async function createScheduledPost(payload) {
  return api.post("/scheduled_posts/", payload);
}

export async function fetchPostStatus(postId) {
  return api.get(`/scheduled_posts/${postId}/status/`);
}

export async function getUploadUrl(fileName, fileType) {
  return api.post("/media/upload_url/", { file_name: fileName, file_type: fileType });
}
