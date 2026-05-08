// Sheriff configuration for architectural boundaries
module.exports = {
  projects: [
    {
      name: 'app',
      root: 'src/app',
      allow: ['shared', 'pages', 'layout'],
    },
    {
      name: 'shared',
      root: 'src/app/shared',
      allow: [],
    },
    {
      name: 'pages',
      root: 'src/app/pages',
      allow: ['shared'],
    },
    {
      name: 'layout',
      root: 'src/app/layout',
      allow: ['shared'],
    }
  ]
};

