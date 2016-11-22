use 64;

# RBX contains the pointer to std::vmcs::data object
# public label is std_vmcs_initialize_guest_vmcs:

  @std_vmcs_data = static std::vmcs::data;
  @std_vmcs_encoding = static std::vmcs::encoding;

std_vmcs_initialize_guest_vmcs_2:
  push rax;       #   save rax because it will get modified
  call $std_vmcs_initialize_16bit_guest_state_2;
  call $std_vmcs_initialize_16bit_host_state_2;
  call $std_vmcs_initialize_64bit_control_2;
  call $std_vmcs_initialize_64bit_guest_state_2;
  call $std_vmcs_initialize_64bit_host_state_2;
  call $std_vmcs_initialize_32bit_control_2;
  call $std_vmcs_initialize_32bit_guest_state_2;
  call $std_vmcs_initialize_32bit_host_state_2;
  call $std_vmcs_initialize_natural_width_control_2;
  call $std_vmcs_initialize_natural_width_guest_state_2;
  call $std_vmcs_initialize_natural_width_host_state_2;
  pop rax;
  ret;

std_vmcs_initialize_16bit_guest_state_2:
  
  mov rax, @std_vmcs_encoding.guest_es_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_es_sel)];
  mov rax, @std_vmcs_encoding.guest_cs_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_cs_sel)];
  mov rax, @std_vmcs_encoding.guest_ss_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ss_sel)];
  mov rax, @std_vmcs_encoding.guest_ds_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ds_sel)];
  mov rax, @std_vmcs_encoding.guest_fs_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_fs_sel)];
  mov rax, @std_vmcs_encoding.guest_gs_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_gs_sel)];
  mov rax, @std_vmcs_encoding.guest_ldtr_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ldtr_sel)];
  mov rax, @std_vmcs_encoding.guest_tr_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_tr_sel)];
  ret;

std_vmcs_initialize_16bit_host_state_2:
  mov rax, @std_vmcs_encoding.host_es_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_es_sel)];
  mov rax, @std_vmcs_encoding.host_cs_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_cs_sel)];
  mov rax, @std_vmcs_encoding.host_ss_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_ss_sel)];
  mov rax, @std_vmcs_encoding.host_ds_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_ds_sel)];
  mov rax, @std_vmcs_encoding.host_fs_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_fs_sel)];
  mov rax, @std_vmcs_encoding.host_gs_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_gs_sel)];
  mov rax, @std_vmcs_encoding.host_tr_sel;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_tr_sel)];
  ret;

std_vmcs_initialize_64bit_control_2:
  mov rax, @std_vmcs_encoding.io_bitmap_a_full;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.io_bitmap_a_full)];
  mov rax, @std_vmcs_encoding.io_bitmap_b_full;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.io_bitmap_b_full)];
  mov rax, @std_vmcs_encoding.msr_bitmap_full;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.msr_bitmap_full)];
  mov rax, @std_vmcs_encoding.exit_msr_store_addr_full;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.exit_msr_store_addr_full)];
  mov rax, @std_vmcs_encoding.entry_msr_load_addr_full;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.entry_msr_load_addr_full)];
  mov rax, @std_vmcs_encoding.executive_vmcs_ptr_full;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.executive_vmcs_ptr_full)];
  mov rax, @std_vmcs_encoding.tsc_offset_full;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.tsc_offset_full)];
  mov rax, @std_vmcs_encoding.virtual_apic_page_addr_full;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.virtual_apic_page_addr_full)];
  mov rax, @std_vmcs_encoding.ept_pointer_full;
  or qword [rbx + disp32 &OFFSET(@std_vmcs_data.ept_pointer_full)], 0x1e;
  vmwrite rax, qword [rbx + disp32 &OFFSET(@std_vmcs_data.ept_pointer_full)];
  ret;

std_vmcs_initialize_64bit_guest_state_2:
   mov rax, @std_vmcs_encoding.vmcs_link_ptr_full;
   vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.vmcs_link_ptr_full)];
   mov rax, @std_vmcs_encoding.guest_ia32_debugctl_full;
   vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_debugctl_full)];
   mov rax, @std_vmcs_encoding.guest_ia32_pat_full;
   vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_pat_full)];
   mov rax, @std_vmcs_encoding.guest_ia32_pdpte0_full;
   vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_pdpte0_full)];
   mov rax, @std_vmcs_encoding.guest_ia32_pdpte1_full;
   vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_pdpte1_full)];
   mov rax, @std_vmcs_encoding.guest_ia32_pdpte2_full;
   vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_pdpte2_full)];
   mov rax, @std_vmcs_encoding.guest_ia32_pdpte3_full;
   vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_pdpte3_full)];
  ret;

std_vmcs_initialize_64bit_host_state_2:
  ret;

std_vmcs_initialize_32bit_control_2:
  mov rax, @std_vmcs_encoding.pin_vm_exec_controls;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.pin_vm_exec_controls)];
  mov rax, @std_vmcs_encoding.proc_vm_exec_controls;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.proc_vm_exec_controls)];
  mov rax, @std_vmcs_encoding.exception_bitmap;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.exception_bitmap)];
  mov rax, @std_vmcs_encoding.pf_ec_mask;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.pf_ec_match)];
  mov rax, @std_vmcs_encoding.cr3_target_count;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr3_target_count)];
  mov rax, @std_vmcs_encoding.exit_controls;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.exit_controls)];
  mov rax, @std_vmcs_encoding.exit_msr_store_count;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.exit_msr_store_count)];
  mov rax, @std_vmcs_encoding.exit_msr_load_count;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.exit_msr_load_count)];
  mov rax, @std_vmcs_encoding.entry_controls;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.entry_controls)];
  mov rax, @std_vmcs_encoding.entry_msr_load_count;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.entry_msr_load_count)];
  mov rax, @std_vmcs_encoding.entry_int_info_field;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.entry_int_info_field)];
  mov rax, @std_vmcs_encoding.entry_exception_ec;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.entry_exception_ec)];
  mov rax, @std_vmcs_encoding.entry_instr_length;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.entry_instr_length)];
  mov rax, @std_vmcs_encoding.tpr_threshold;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.tpr_threshold)];
  mov rax, @std_vmcs_encoding.proc_vm_exec_controls2;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.proc_vm_exec_controls2)];
  ret;

std_vmcs_initialize_32bit_guest_state_2:
  mov rax, @std_vmcs_encoding.guest_es_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_es_limit)];
  mov rax, @std_vmcs_encoding.guest_cs_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_cs_limit)];
  mov rax, @std_vmcs_encoding.guest_ss_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ss_limit)];
  mov rax, @std_vmcs_encoding.guest_ds_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ds_limit)];
  mov rax, @std_vmcs_encoding.guest_fs_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_fs_limit)];
  mov rax, @std_vmcs_encoding.guest_gs_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_gs_limit)];
  mov rax, @std_vmcs_encoding.guest_ldtr_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ldtr_limit)];
  mov rax, @std_vmcs_encoding.guest_tr_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_tr_limit)];
  mov rax, @std_vmcs_encoding.guest_gdtr_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_gdtr_limit)];
  mov rax, @std_vmcs_encoding.guest_idtr_limit;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_idtr_limit)];
  mov rax, @std_vmcs_encoding.guest_es_attr;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_es_attr)];
  mov rax, @std_vmcs_encoding.guest_cs_attr;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_cs_attr)];
  mov rax, @std_vmcs_encoding.guest_ss_attr;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ss_attr)];
  mov rax, @std_vmcs_encoding.guest_ds_attr;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ds_attr)];
  mov rax, @std_vmcs_encoding.guest_fs_attr;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_fs_attr)];
  mov rax, @std_vmcs_encoding.guest_gs_attr;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_gs_attr)];
  mov rax, @std_vmcs_encoding.guest_ldtr_attr;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ldtr_attr)];
  mov rax, @std_vmcs_encoding.guest_tr_attr;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_tr_attr)];
  mov rax, @std_vmcs_encoding.guest_interruptibility_info;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_interruptibility_info)];
  mov rax, @std_vmcs_encoding.guest_activity_state;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_activity_state)];
  mov rax, @std_vmcs_encoding.guest_smbase;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_smbase)];
  mov rax, @std_vmcs_encoding.guest_ia32_sysenter_cs;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_sysenter_cs)];
  ret;

std_vmcs_initialize_32bit_host_state_2:
  mov rax, @std_vmcs_encoding.host_ia32_sysenter_cs;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_ia32_sysenter_cs)];
  ret;

std_vmcs_initialize_natural_width_control_2:
  mov rax, @std_vmcs_encoding.cr0_mask;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr0_mask)];
  mov rax, @std_vmcs_encoding.cr4_mask;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr4_mask)];
  mov rax, @std_vmcs_encoding.cr0_read_shadow;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr0_read_shadow)];
  mov rax, @std_vmcs_encoding.cr4_read_shadow;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr4_read_shadow)];
  mov rax, @std_vmcs_encoding.cr3_target_2;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr3_target_2)];
  mov rax, @std_vmcs_encoding.cr3_target_1;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr3_target_1)];
  mov rax, @std_vmcs_encoding.cr3_target_2;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr3_target_2)];
  mov rax, @std_vmcs_encoding.cr3_target_3;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.cr3_target_3)];
  ret;

std_vmcs_initialize_natural_width_guest_state_2:
  mov rax, @std_vmcs_encoding.guest_cr0;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_cr0)];
  mov rax, @std_vmcs_encoding.guest_cr3;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_cr3)];
  mov rax, @std_vmcs_encoding.guest_cr4;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_cr4)];
  mov rax, @std_vmcs_encoding.guest_es_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_es_base)];
  mov rax, @std_vmcs_encoding.guest_cs_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_cs_base)];
  mov rax, @std_vmcs_encoding.guest_ss_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ss_base)];
  mov rax, @std_vmcs_encoding.guest_ds_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ds_base)];
  mov rax, @std_vmcs_encoding.guest_fs_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_fs_base)];
  mov rax, @std_vmcs_encoding.guest_gs_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_gs_base)];
  mov rax, @std_vmcs_encoding.guest_ldtr_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ldtr_base)];
  mov rax, @std_vmcs_encoding.guest_tr_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_tr_base)];
  mov rax, @std_vmcs_encoding.guest_gdtr_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_gdtr_base)];
  mov rax, @std_vmcs_encoding.guest_idtr_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_idtr_base)];
  mov rax, @std_vmcs_encoding.guest_dr7;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_dr7)];
  mov rax, @std_vmcs_encoding.guest_rsp;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_rsp)];
  mov rax, @std_vmcs_encoding.guest_rip;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_rip)];
  mov rax, @std_vmcs_encoding.guest_rflags;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_rflags)];
  mov rax, @std_vmcs_encoding.guest_pending_debug_except;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_pending_debug_except)];
  mov rax, @std_vmcs_encoding.guest_ia32_sysenter_esp;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_sysenter_esp)];
  mov rax, @std_vmcs_encoding.guest_ia32_sysenter_eip;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.guest_ia32_sysenter_eip)];
  ret;

std_vmcs_initialize_natural_width_host_state_2:
  mov rax, @std_vmcs_encoding.host_cr0;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_cr0)];
  mov rax, @std_vmcs_encoding.host_cr3;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_cr3)];
  mov rax, @std_vmcs_encoding.host_cr4;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_cr4)];
  mov rax, @std_vmcs_encoding.host_fs_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_fs_base)];
  mov rax, @std_vmcs_encoding.host_gs_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_gs_base)];
  mov rax, @std_vmcs_encoding.host_tr_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_tr_base)];
  mov rax, @std_vmcs_encoding.host_gdtr_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_gdtr_base)];
  mov rax, @std_vmcs_encoding.host_idtr_base;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_idtr_base)];
  mov rax, @std_vmcs_encoding.host_ia32_sysenter_esp;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_ia32_sysenter_esp)];
  mov rax, @std_vmcs_encoding.host_ia32_sysenter_eip;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_ia32_sysenter_eip)];
  mov rax, @std_vmcs_encoding.host_rsp;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_rsp)];
  mov rax, @std_vmcs_encoding.host_rip;
  vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_rip)];
  ret;

END;

