import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://10.37.117.197:5000",
  timeout: 5000,
});

export default axiosInstance;
