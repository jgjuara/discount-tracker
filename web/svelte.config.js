import adapter from '@sveltejs/adapter-static';

const prod = process.env.NODE_ENV === 'production' || process.argv.includes('build') || process.argv.some(arg => arg.includes('prerender'));

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
		runes: ({ filename }) => filename.split(/[/\\]/).includes('node_modules') ? undefined : true
	},
	kit: {
		adapter: adapter(),
		paths: {
			base: prod ? '/discount-tracker' : ''
		}
	}
};

export default config;
