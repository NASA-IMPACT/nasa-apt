import React, { Component } from 'react';

class UhOh extends Component {
  render() {
    return (
      <div>
        <h1>Page not found</h1>
        <div>
          <p>We were not able to find the page you are looking for. It may have been archived or removed.</p>
          <p>If you think this page should be here let us know via <a href='mailto:' title='Send us an email'>email</a>.</p>
          <p><a href='/' title='Visit the homepage'>Visit the homepage</a>.</p>
        </div>
      </div>
    );
  }
}

export default UhOh;
