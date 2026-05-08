// Sheriff configuration for architectural boundaries
module.exports = {
  projects: [
    {
      name: 'app',
      root: 'src/app',
      allow: ['shared', 'pages', 'layout', 'core'],
    },
    {
      name: 'core',
      root: 'src/app/core',
      allow: [],
    },
    {
      name: 'shared',
      root: 'src/app/shared',
      allow: [],
    },
    {
      name: 'pages',
      root: 'src/app/pages',
      allow: ['shared', 'core'],
    },
    {
      name: 'layout',
      root: 'src/app/layout',
      allow: ['shared', 'core'],
    }
  ]
};
