package com.example.usermanagement.service;

import com.example.usermanagement.dto.LoginRequest;
import com.example.usermanagement.dto.LoginResponse;
import com.example.usermanagement.entity.User;
import com.example.usermanagement.exception.DuplicateResourceException;
import com.example.usermanagement.exception.ResourceNotFoundException;
import com.example.usermanagement.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class UserService {

    private final UserRepository userRepository;

    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User createUser(User user) {
        try {
            return userRepository.save(user);
        } catch (DataIntegrityViolationException e) {
            // Handle unique constraint violations from database
            String rootCause = e.getRootCause() != null ? e.getRootCause().getMessage() : e.getMessage();
            if (rootCause != null) {
                String lowerMessage = rootCause.toLowerCase();
                if (lowerMessage.contains("username") || lowerMessage.contains("'username'")) {
                    throw new DuplicateResourceException("用户名已存在: " + user.getUsername());
                } else if (lowerMessage.contains("email") || lowerMessage.contains("'email'")) {
                    throw new DuplicateResourceException("邮箱已存在: " + user.getEmail());
                }
            }
            throw new DuplicateResourceException("数据已存在，无法创建");
        }
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    public Optional<User> getUserById(Long id) {
        return userRepository.findById(id);
    }

    public User updateUser(Long id, User userDetails) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("用户不存在，ID: " + id));

        user.setUsername(userDetails.getUsername());
        user.setEmail(userDetails.getEmail());
        if (userDetails.getPassword() != null && !userDetails.getPassword().isEmpty()) {
            user.setPassword(userDetails.getPassword());
        }
        
        try {
            return userRepository.save(user);
        } catch (DataIntegrityViolationException e) {
            // Handle unique constraint violations from database
            String rootCause = e.getRootCause() != null ? e.getRootCause().getMessage() : e.getMessage();
            if (rootCause != null) {
                String lowerMessage = rootCause.toLowerCase();
                if (lowerMessage.contains("username") || lowerMessage.contains("'username'")) {
                    throw new DuplicateResourceException("用户名已存在: " + userDetails.getUsername());
                } else if (lowerMessage.contains("email") || lowerMessage.contains("'email'")) {
                    throw new DuplicateResourceException("邮箱已存在: " + userDetails.getEmail());
                }
            }
            throw new DuplicateResourceException("数据已存在，无法更新");
        }
    }

    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new ResourceNotFoundException("用户不存在，ID: " + id);
        }
        userRepository.deleteById(id);
    }

    public LoginResponse login(LoginRequest loginRequest) {
        Optional<User> userOptional = userRepository.findByUsername(loginRequest.getUsername());
        
        if (userOptional.isEmpty()) {
            return new LoginResponse(false, "用户名或密码错误", null, null);
        }
        
        User user = userOptional.get();
        
        if (!user.getPassword().equals(loginRequest.getPassword())) {
            return new LoginResponse(false, "用户名或密码错误", null, null);
        }
        
        return new LoginResponse(true, "登录成功", user.getId(), user.getUsername());
    }
}
