// ChatList.js
import React,{useState} from 'react';
import { BarsOutlined } from '@ant-design/icons';

const ChatList = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);
  
    const toggleCollapse = () => {
      setIsCollapsed(!isCollapsed);
    };
  
    return (
      <div className={`flex flex-col ${isCollapsed ? 'w-16' : 'w-1/4'} transition-all duration-300 bg-gray-200`}>
        <div className="flex justify-between items-center p-4">
          {!isCollapsed && <h2 className="text-xl font-bold mb-4">All Chats</h2>}
          <button onClick={toggleCollapse} className="p-2 focus:outline-none">
            {isCollapsed ? <BarsOutlined /> : <BarsOutlined />}
          </button>
        </div>
        {!isCollapsed && (
        <ul className="ml-4">
            <li className="mb-2">Chat 1</li>
            <li className="mb-2">Chat 2</li>
            <li className="mb-2">Chat 3</li>
          </ul>
        )}
      </div>
    );
  };
  
  export default ChatList;
