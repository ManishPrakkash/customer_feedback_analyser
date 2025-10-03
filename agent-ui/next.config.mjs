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
	// Map "@" to the project root without relying on __dirname (ESM-safe)
	webpack: (config) => {
		config.resolve.alias = {
			...(config.resolve.alias || {}),
			"@": config.context,
		};
		return config;
	},
};

export default nextConfig;

