import axios from 'axios'


const makeRequest = ({method='get', url, data=null}) => {
  return axios({
    method,
    url: `${process.env.REACT_APP_WEB_SERVICE_URL}${url}`,
    data
  })
}

export default makeRequest
