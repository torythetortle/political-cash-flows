import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: undefined
		}),
		paths: {
			base: process.env.BASE_PATH || ''
		},
		prerender: {
			handleHttpError: 'warn',
			handleMissingId: 'warn'
		}
	}
};

export default config;
