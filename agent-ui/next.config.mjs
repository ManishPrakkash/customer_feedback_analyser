import path from "path";
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
	eslint: {
		ignoreDuringBuilds: true,
	},
	experimental: {
		tsconfigPaths: true,
	},
	// Map "@" to the project root without relying on __dirname (ESM-safe)
	webpack: (config) => {
		config.resolve.alias = {
			...(config.resolve.alias || {}),
			"@": path.resolve(process.cwd()),
		};
		return config;
	},
};

export default nextConfig;

