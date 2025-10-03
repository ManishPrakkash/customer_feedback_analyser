import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
	images: {
		remotePatterns: [
			{
				protocol: "https",
				hostname: "avatars.githubusercontent.com",
				port: "",
				pathname: "**",
			},
		],
	},
	webpack: config => {
		// Ensure path alias '@/...' works at build/runtime (in addition to tsconfig paths)
		config.resolve.alias = {
			...(config.resolve.alias || {}),
			"@": path.resolve(__dirname, "./"),
		};
		return config;
	},
};

export default nextConfig;

