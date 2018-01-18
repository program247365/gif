module.exports = {
    siteMetadata: {
      title: `lulzgif`,
    },
    plugins: [
      {
        resolve: `gatsby-source-filesystem`,
        options: {
          name: `src`,
          path: `${__dirname}/static/`,
        },
      },
      `gatsby-plugin-react-helmet`,
      {
        resolve: `gatsby-plugin-favicon`,
        options: {
          logo: './src/images/favicon.png',
          injectHTML: true,
          icons: {
            android: true,
            appleIcon: true,
            appleStartup: true,
            coast: false,
            favicons: true,
            firefox: true,
            twitter: false,
            yandex: false,
            windows: false
          }
        }
      }
    ],
  }