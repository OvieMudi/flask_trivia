import React, { Component } from 'react';
// import logo from '../logo.svg';
import '../stylesheets/Header.css';

class Header extends Component {
  navTo(uri) {
    window.location.href = window.location.origin + uri;
  }

  render() {
    return (
      <div className="App-header">
        <h1
          onClick={() => {
            this.navTo('');
          }}
          className="pointer"
        >
          Udacitrivia
        </h1>
        <h2
          onClick={() => {
            this.navTo('');
          }}
          className="pointer scale"
        >
          List
        </h2>
        <h2
          onClick={() => {
            this.navTo('/add');
          }}
          className="pointer scale"
        >
          Add
        </h2>
        <h2
          onClick={() => {
            this.navTo('/play');
          }}
          className="pointer scale"
        >
          Play
        </h2>
      </div>
    );
  }
}

export default Header;
