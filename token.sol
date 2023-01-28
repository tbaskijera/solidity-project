// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract Token {
    address public owner;
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Burn(address indexed burner, uint256 value);
    event Mint(address indexed minter, uint256 value);

    constructor(
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _totalSupply
    ) {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        totalSupply = _totalSupply;
        balanceOf[msg.sender] = _totalSupply;
    }

    function checkBalance(address _owner) public view returns (uint256) {
        return balanceOf[_owner];
    }

    function transfer(address _to, uint256 _value) public payable {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance!");
        require(_value > 0, "Transfer value can not be 0!");

        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
    }

    function mint(uint256 _value) public {
        require(msg.sender == owner, "Only owner can mint tokens!");
        require(_value > 0, "Mint value can not be 0!");
        totalSupply += _value;
        balanceOf[msg.sender] += _value;
        emit Mint(msg.sender, _value);
    }

    function burn(uint256 _value) public {
        require(msg.sender == owner, "Only owner can burn tokens!");
        require(
            balanceOf[msg.sender] >= _value,
            "Burn value can't be higher than balance!"
        );
        require(_value > 0, "Burn value can not be 0!");

        balanceOf[msg.sender] -= _value;
        totalSupply -= _value;
        emit Burn(msg.sender, _value);
    }
}
