module.exports = function(api) {
    api.cache(true);

    return {
        presets: [
            ["babel-preset-expo", {
            jsxImportSource: "nativewind"
            }], 
            "nativewind/babel"
        ],

        plugins: [["module-resolver", {
            root: ["./"],

            alias: {
                "@": "./src",
                "@/components": "./src/components",
                "@/features": "./src/features",
                "@/hooks": "./src/hooks",
                "@/services": "./src/services",
                "@/utils": "./src/utils",
                "@/theme": "./src/theme",
                "@/types": "./src/types",
                "@/assets": "./src/assets",
                "@/navigation": "./src/navigation",
                "tailwind.config": "./tailwind.config.js"
            }
        }]]
    };
};