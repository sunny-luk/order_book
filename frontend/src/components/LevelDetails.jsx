import React from 'react'
import PropTypes from 'prop-types'
import Modal from 'react-bootstrap/Modal'
import Table from 'react-bootstrap/Table'

const LevelDetails = (props) => {

  const { show, setShow } = props

  const onHide = () => {
    setShow(false)
  }


  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header>Order Level</Modal.Header>
      <Modal.Body>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Price</th>
            <th>Quantity</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          {renderLevels()}
        </tbody>
    </Table>
      </Modal.Body>
    </Modal>
  )
}

LevelDetails.propTypes = {
  show: PropTypes.bool.isRequired,
  setShow: PropTypes.func.isRequired
}

export default LevelDetails