import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import Navbar from './components/Navbar'
import Mainpage from './components/Mainpage'
import Querypage from './components/Querypage'

function App() {
  const[Connectionstatus, setConnectionstatus] = useState(false);
  const[ConnectionName,setConnectionName]=useState('')
  const[ConnectionURL,setConnectionURL]=useState('')
  return (
    <>
      <Navbar connectionStatus={Connectionstatus} connectionName={ConnectionName} />
      {
        !Connectionstatus ? 
        <>
          <Mainpage setConnectionstatus={setConnectionstatus} setConnectionName={setConnectionName} setConnectionURL={setConnectionURL}/>
        </>:
        <Querypage ConnectionName={ConnectionName} ConnectionString={ConnectionURL}/>
      }
    </>
  )
}

export default App
