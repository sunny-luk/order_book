import React from 'react'
import PropType from 'prop-types'
import Button from 'react-bootstrap/Button'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'


const ActionBar = (props) => {
  return (
    <Row>
      <Col xs={12} md={{span: 6, offset: 3}} lg={{span: 4, offset: 4}}>
        <Button block variant='info' onClick={() => props.setShowCreateForm(true)}>New order</Button>
      </Col>
    </Row>
    
  )
}

ActionBar.propTypes = {
  showCreateForm: PropType.func.isRequired
}

export default ActionBar