import React, { Component } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import UsersList from "./components/UsersList";

class App extends Component {
  constructor() {
    super();

    this.state = {
      users: []
    };
  }

  getUsers() {
    axios
      .get(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`)
      .then(res => console.log(this.setState({ users: res.data.data.users })))
      .catch(err => console.log(err));
  }

  render() {
    return (
      <section className="section">
        <div className="container">
          <div className="columns">
            <div className="column is-one-third">
              <br />
              <h1 className="title is-1 is-1">All Users</h1>
              <hr />
              <br />
              <UsersList users={this.state.user} />
            </div>
          </div>
        </div>
      </section>
    );
  }

  componentDidMount() {
    this.getUsers();
  }
}

ReactDOM.render(<App />, document.getElementById("root"));
