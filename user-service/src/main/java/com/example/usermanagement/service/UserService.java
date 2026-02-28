package com.example.usermanagement.service;

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
            String message = e.getMessage();
            if (message != null && message.toLowerCase().contains("username")) {
                throw new DuplicateResourceException("用户名已存在: " + user.getUsername());
            } else if (message != null && message.toLowerCase().contains("email")) {
                throw new DuplicateResourceException("邮箱已存在: " + user.getEmail());
            } else {
                throw new DuplicateResourceException("数据已存在，无法创建");
            }
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
        
        try {
            return userRepository.save(user);
        } catch (DataIntegrityViolationException e) {
            // Handle unique constraint violations from database
            String message = e.getMessage();
            if (message != null && message.toLowerCase().contains("username")) {
                throw new DuplicateResourceException("用户名已存在: " + userDetails.getUsername());
            } else if (message != null && message.toLowerCase().contains("email")) {
                throw new DuplicateResourceException("邮箱已存在: " + userDetails.getEmail());
            } else {
                throw new DuplicateResourceException("数据已存在，无法更新");
            }
        }
    }

    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new ResourceNotFoundException("用户不存在，ID: " + id);
        }
        userRepository.deleteById(id);
    }
}
