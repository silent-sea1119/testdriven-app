import React from "react";

const AddUser = props => (
  <form onSubmit={props.addUser}>
    <div className="field">
      <input
        name="username"
        className="input is-large"
        type="text"
        placeholder="Enter a username"
        required
        value={props.username}
        onChange={props.handleChange}
      />
    </div>
    <div className="field">
      <input
        name="email"
        className="input is-large"
        type="email"
        placeholder="Enter an email address"
        required
        value={props.email}
        onChange={props.handleChange}
      />
    </div>
    <div className="field">
      <input
        className="button is-primary is-fullwidth is-large"
        type="submit"
        value="Submit"
      />
    </div>
  </form>
);

export default AddUser;
