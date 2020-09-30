import React, { Component } from 'react'

class Search extends Component {
  state = {
    query: '',
  }

  getInfo = (event) => {
    event.preventDefault();
    //by default search start from page 1
    this.props.submitSearch(this.state.query,1)
  }

  handleInputChange = () => {
    this.setState({
      query: this.search.value
    })
  }

  render() {
    return (
      <form onSubmit={this.getInfo}>
        <input
          placeholder="Search questions..."
          ref={input => this.search = input}
          onChange={this.handleInputChange}
        />
        <input type="submit" value="Submit" className="button"/>
      </form>
    )
  }
}

export default Search
