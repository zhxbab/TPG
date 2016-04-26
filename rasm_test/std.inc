
################ descriptors #################
struct std::table_pointer {
  uint16 limit = 0x100;   
  uint64 base;
}

bitstruct std::descriptor, 64 {
  15..0  limit = 0xfffff;
  39..16 base  = 0x0;
  43..40 type = 0x0;
  44..44 s    = 0x1;
  46..45 dpl  = 0x0;
  47..47 p    = 0x1;
  51..48 limit(19..16);
  52 avl;
  53 l;
  54 db = 0;
  55 g = 1;
  63..56 base(31..24) = 0;
}


################ interrupt gates #################
bitstruct std::idt_gate_64, 128 {
  15..0  offset;
  31..16 selector;
  34..32 ist;
  43..40 type = 0xE;
  46..45 dpl = 0;
  47..47 p = 1;
  63..48 offset(31..16);
  95..64 offset(63..32);
}

bitstruct std::idt_gate_32, 64 {
  15..0  offset;
  31..16 selector;
  34..32 ist;
  43..40 type = 0xE;
  46..45 dpl = 0;
  47..47 p = 1;
  63..48 offset(31..16);
}


################ vmcs  #################

struct  std::vmcs {
  uint64 data[1024];  # allocated 8096 (0x2000) memory for each vmcs 04
}

struct  std::vmcs::data {
  # 16 bit control field
  uint16 vpid;
  uint16 posted_intr_notification_vector;
  uint16 eptp_index;

  # 16 bit Guest-State fields
  uint32 guest_es_sel;
  uint32 guest_cs_sel;
  uint32 guest_ss_sel;
  uint32 guest_ds_sel;
  uint32 guest_fs_sel;
  uint32 guest_gs_sel;
  uint32 guest_ldtr_sel;
  uint32 guest_tr_sel;
  uint32 guest_interrupt_status;

  # 16 bit Host-State fields
  uint32 host_es_sel;
  uint32 host_cs_sel;
  uint32 host_ss_sel;
  uint32 host_ds_sel;
  uint32 host_fs_sel;
  uint32 host_gs_sel;
  uint32 host_tr_sel;

  # 64 bit Control fields
  uint32 io_bitmap_a_full; 
  uint32 io_bitmap_a_high; 
  uint32 io_bitmap_b_full; 
  uint32 io_bitmap_b_high; 
  uint32 msr_bitmap_full; 
  uint32 msr_bitmap_high; 
  uint32 exit_msr_store_addr_full; 
  uint32 exit_msr_store_addr_high; 
  uint32 exit_msr_load_addr_full; 
  uint32 exit_msr_load_addr_high; 
  uint32 entry_msr_load_addr_full; 
  uint32 entry_msr_load_addr_high; 
  uint32 executive_vmcs_ptr_full; 
  uint32 executive_vmcs_ptr_high; 
  uint32 tsc_offset_full; 
  uint32 tsc_offset_high; 
  uint32 virtual_apic_page_addr_full; 
  uint32 virtual_apic_page_addr_high;
  uint32 apic_access_addr_full;
  uint32 apic_access_addr_high;
  uint32 posted_intr_descriptor_addr_full;
  uint32 posted_intr_descriptor_addr_high;
  uint32 vm_function_controls_full;
  uint32 vm_function_controls_high;
  uint32 ept_pointer_full;
  uint32 ept_pointer_high;  
  uint32 eoi_exit_bimap_0_full;
  uint32 eoi_exit_bimap_0_high;
  uint32 eoi_exit_bimap_1_full;
  uint32 eoi_exit_bimap_1_high;
  uint32 eoi_exit_bimap_2_full;
  uint32 eoi_exit_bimap_2_high;
  uint32 eoi_exit_bimap_3_full;
  uint32 eoi_exit_bimap_3_high;
  uint32 eptp_list_addr_full;
  uint32 eptp_list_addr_high;
  uint32 vmread_bitmap_addr_full;
  uint32 vmread_bitmap_addr_high;
  uint32 vmwrite_bitmap_addr_full;
  uint32 vmwrite_bitmap_addr_high;
  uint32 virtualization_exception_info_addr_full;
  uint32 virtualization_exception_info_addr_high;
  uint32 xss_exiting_bitmap_full;
  uint32 xss_exiting_bitmap_high;
  uint32 tsc_multiplier_full;
  uint32 tsc_multiplier_high;

  # 64 bit read-only data fields
  uint32 guest_physical_addr_full;
  uint32 guest_physical_addr_high;

  # 64 bit guest-state fields
  uint32 vmcs_link_ptr_full = 0xffffffff; 
  uint32 vmcs_link_ptr_high = 0xffffffff; 
  uint32 guest_ia32_debugctl_full;  
  uint32 guest_ia32_debugctl_high;  
  uint32 guest_ia32_path_full;
  uint32 guest_ia32_path_high;
  uint32 guest_ia32_efer_full;
  uint32 guest_ia32_efer_high;
  uint32 guest_ia32_perf_ctl_full;
  uint32 guest_ia32_perf_ctl_high;
  uint32 guest_ia32_pdpte0_full;
  uint32 guest_ia32_pdpte0_high;
  uint32 guest_ia32_pdpte1_full;
  uint32 guest_ia32_pdpte1_high;
  uint32 guest_ia32_pdpte2_full;
  uint32 guest_ia32_pdpte2_high;
  uint32 guest_ia32_pdpte3_full;
  uint32 guest_ia32_pdpte3_high;

  # 64 bit host-state fields
  uint32 host_ia32_pat_full;
  uint32 host_ia32_pat_high;
  uint32 host_ia32_efer_full;
  uint32 host_ia32_efer_high;
  uint32 host_ia32_perf_ctl_full;
  uint32 host_ia32_perf_ctl_high;

  # 32 bit control fields
  uint32 pin_vm_exec_controls    = 0x1e;
  uint32 proc_vm_exec_controls   = 0x8401e172;
  uint32 exception_bitmap        = 0xffffffff;
  uint32 pf_ec_mask;
  uint32 pf_ec_match;
  uint32 cr3_target_count        = 1;
  uint32 exit_controls           = 0x00036fff;
  uint32 exit_msr_store_count;
  uint32 exit_msr_load_count ;
  uint32 entry_controls          = 0x000013ff;
  uint32 entry_msr_load_count;
  uint32 entry_int_info_field;
  uint32 entry_exception_ec;
  uint32 entry_instr_length;
  uint32 tpr_threshold;
  uint32 proc_vm_exec_controls2  = 0x2;  # EPT is on
  uint32 ple_gap;
  uint32 ple_window;

  # 32 bit read only data fields 
  uint32 instr_error;
  uint32 exit_reason;
  uint32 int_info;
  uint32 int_ec;
  uint32 idt_vec_info_field;
  uint32 idt_vec_ec;
  uint32 exit_instr_len;
  uint32 exit_instr_info;


  # 32 bit guest-state fields
  uint32 guest_es_limit = 0xffffffff;
  uint32 guest_cs_limit = 0xffffffff; 
  uint32 guest_ss_limit = 0xffffffff; 
  uint32 guest_ds_limit = 0xffffffff; 
  uint32 guest_fs_limit = 0xffffffff; 
  uint32 guest_gs_limit = 0xffffffff; 
  uint32 guest_ldtr_limit; 
  uint32 guest_tr_limit = 0x77; 
  uint32 guest_gdtr_limit = 0xffff; 
  uint32 guest_idtr_limit = 0xffff; 
  uint32 guest_es_attr = 0xc093; 
  uint32 guest_cs_attr = 0xa09b; 
  uint32 guest_ss_attr = 0xc093; 
  uint32 guest_ds_attr = 0xc093; 
  uint32 guest_fs_attr = 0xc093; 
  uint32 guest_gs_attr = 0xc093; 
  uint32 guest_ldtr_attr = 0x10000; 
  uint32 guest_tr_attr = 0x8b; 
  uint32 guest_interruptibility_info;
  uint32 guest_activity_state;
  uint32 guest_smbase;
  uint32 guest_ia32_sysenter_cs;
  uint32 preemption_timer_value;

  # 32 bit host-state fields
  uint32 host_ia32_sysenter_cs;
  
  # natural-width control fields
  uint64 cr0_mask;
  uint64 cr4_mask;
  uint64 cr0_read_shadow;
  uint64 cr4_read_shadow;
  uint64 cr3_target_0;
  uint64 cr3_target_1;
  uint64 cr3_target_2;
  uint64 cr3_target_3;

  # natural-width read only fields 
  uint32 exit_qualification;
  uint32 io_rcx;
  uint32 io_rsi;
  uint32 io_rdi;
  uint32 io_rip;
  uint32 guest_linear_addr;


  # nature-width guest-state fields
  uint64 guest_cr0 = 0x80000031;
  uint64 guest_cr3 = 0xB000;
  uint64 guest_cr4 = 0x2620;
  uint64 guest_es_base;
  uint64 guest_cs_base;
  uint64 guest_ss_base;
  uint64 guest_ds_base;
  uint64 guest_fs_base;
  uint64 guest_gs_base;
  uint64 guest_ldtr_base;
  uint64 guest_tr_base;
  uint64 guest_gdtr_base;
  uint64 guest_idtr_base;
  uint64 guest_dr7;
  uint64 guest_rsp;
  uint64 guest_rip;
  uint64 guest_rflags = 0x2;   # default 0x2 is default
  uint64 guest_pending_debug_except;
  uint64 guest_ia32_sysenter_esp;
  uint64 guest_ia32_sysenter_eip;

  # nature-width host-state fields
  uint64 host_cr0 = 0x80000031 ;
  uint64 host_cr3 = 0x7000;
  uint64 host_cr4 = 0x2620;
  uint64 host_fs_base;
  uint64 host_gs_base;
  uint64 host_tr_base;
  uint64 host_gdtr_base;
  uint64 host_idtr_base;
  uint64 host_ia32_sysenter_esp;
  uint64 host_ia32_sysenter_eip;
  uint64 host_rsp;
  uint64 host_rip;
}

######### DEFINES ##############
struct  std::vmcs::encoding {
  # 16 bit control field
  uint32 vpid =     0x0;
  uint32 posted_intr_notification_vector = 0x2;
  uint32 eptp_index =   0x4;

  # 16 bit Guest-State fields
  uint32 guest_es_sel           = 0x800;
  uint32 guest_cs_sel           = 0x802;
  uint32 guest_ss_sel           = 0x804;
  uint32 guest_ds_sel           = 0x806;
  uint32 guest_fs_sel           = 0x808;
  uint32 guest_gs_sel           = 0x80a;
  uint32 guest_ldtr_sel         = 0x80c;
  uint32 guest_tr_sel           = 0x80e;
  uint32 guest_interrupt_status = 0x810;


  # 16 bit Host-State fields
  uint32 host_es_sel = 0xc00;
  uint32 host_cs_sel = 0xc02;
  uint32 host_ss_sel = 0xc04;
  uint32 host_ds_sel = 0xc06;
  uint32 host_fs_sel = 0xc08;
  uint32 host_gs_sel = 0xc0a;
  uint32 host_tr_sel = 0xc0c;

  # 64 bit Control fields
  uint32 io_bitmap_a_full = 0x2000;
  uint32 io_bitmap_a_high = 0x2001;
  uint32 io_bitmap_b_full = 0x2002;
  uint32 io_bitmap_b_high = 0x2003;
  uint32 msr_bitmap_full  = 0x2004;
  uint32 msr_bitmap_high  = 0x2005;
  uint32 exit_msr_store_addr_full = 0x2006;
  uint32 exit_msr_store_addr_high = 0x2007;
  uint32 exit_msr_load_addr_full =  0x2008;
  uint32 exit_msr_load_addr_high =  0x2009;
  uint32 entry_msr_load_addr_full = 0x200a;
  uint32 entry_msr_load_addr_high = 0x200b;
  uint32 executive_vmcs_ptr_full =  0x200c;
  uint32 executive_vmcs_ptr_high =  0x200d;
  uint32 tsc_offset_full         =  0x2010;
  uint32 tsc_offset_high         =  0x2011;
  uint32 virtual_apic_page_addr_full      = 0x2012;
  uint32 virtual_apic_page_addr_high      = 0x2013;
  uint32 apic_access_addr_full            = 0x2014;
  uint32 apic_access_addr_high            = 0x2015;
  uint32 posted_intr_descriptor_addr_full = 0x2016;
  uint32 posted_intr_descriptor_addr_high = 0x2017;
  uint32 vm_function_controls_full        = 0x2018;
  uint32 vm_function_controls_high        = 0x2019;
  uint32 ept_pointer_full                 = 0x201a;
  uint32 ept_pointer_high                 = 0x201b;
  uint32 eoi_exit_bimap_0_full            = 0x201c;
  uint32 eoi_exit_bimap_0_high            = 0x201d;
  uint32 eoi_exit_bimap_1_full            = 0x201e;
  uint32 eoi_exit_bimap_1_high            = 0x201f;
  uint32 eoi_exit_bimap_2_full            = 0x2020;
  uint32 eoi_exit_bimap_2_high            = 0x2021;
  uint32 eoi_exit_bimap_3_full            = 0x2022;
  uint32 eoi_exit_bimap_3_high            = 0x2023;
  uint32 eptp_list_addr_full              = 0x2024;
  uint32 eptp_list_addr_high              = 0x2025;
  uint32 vmread_bitmap_addr_full          = 0x2026;
  uint32 vmread_bitmap_addr_high          = 0x2027;
  uint32 vmwrite_bitmap_addr_full         = 0x2028;
  uint32 vmwrite_bitmap_addr_high         = 0x2029;
  uint32 virtualization_exception_info_addr_full = 0x202a;
  uint32 virtualization_exception_info_addr_high = 0x020b;
  uint32 xss_exiting_bitmap_full          = 0x202c;
  uint32 xss_exiting_bitmap_high          = 0x202d;
  uint32 tsc_multiplier_full              = 0x2032;
  uint32 tsc_multiplier_high              = 0x2033;

  # 64 bit read-only data fields
  uint32 guest_physical_addr_full         = 0x2400;
  uint32 guest_physical_addr_high         = 0x2401;
  
  # 64 bit guest-state fields
  uint32 vmcs_link_ptr_full      = 0x2800;  
  uint32 vmcs_link_ptr_high      = 0x2801;  
  uint32 guest_ia32_debugctl_full= 0x2802;  
  uint32 guest_ia32_debugctl_high= 0x2803;  
  uint32 guest_ia32_path_full    = 0x2804;
  uint32 guest_ia32_path_high    = 0x2805;
  uint32 guest_ia32_efer_full    = 0x2806;
  uint32 guest_ia32_efer_high    = 0x2807;
  uint32 guest_ia32_perf_ctl_full= 0x2808;
  uint32 guest_ia32_perf_ctl_high= 0x2809;
  uint32 guest_ia32_pdpte0_full  = 0x280a;
  uint32 guest_ia32_pdpte0_high  = 0x280b;
  uint32 guest_ia32_pdpte1_full  = 0x280c;
  uint32 guest_ia32_pdpte1_high  = 0x280d;
  uint32 guest_ia32_pdpte2_full  = 0x280e;
  uint32 guest_ia32_pdpte2_high  = 0x280f;
  uint32 guest_ia32_pdpte3_full  = 0x2810;
  uint32 guest_ia32_pdpte3_high  = 0x2811;

  # 64 bit host-state fields
  uint32 host_ia32_pat_full     = 0x2c00;
  uint32 host_ia32_pat_high     = 0x2c01;
  uint32 host_ia32_efer_full    = 0x2c02;
  uint32 host_ia32_efer_high    = 0x2c03;
  uint32 host_ia32_perf_ctl_full= 0x2c04;
  uint32 host_ia32_perf_ctl_high= 0x2c05;

  # 32 bit control fields
  uint32 pin_vm_exec_controls    = 0x4000;
  uint32 proc_vm_exec_controls   = 0x4002;
  uint32 exception_bitmap        = 0x4004;
  uint32 pf_ec_mask              = 0x4006;
  uint32 pf_ec_match             = 0x4008;
  uint32 cr3_target_count        = 0x400a;
  uint32 exit_controls           = 0x400c;
  uint32 exit_msr_store_count    = 0x400e;
  uint32 exit_msr_load_count     = 0x4010;
  uint32 entry_controls          = 0x4012;
  uint32 entry_msr_load_count    = 0x4014;
  uint32 entry_int_info_field    = 0x4016;
  uint32 entry_exception_ec      = 0x4018;
  uint32 entry_instr_length      = 0x401a;
  uint32 tpr_threshold           = 0x401c;
  uint32 proc_vm_exec_controls2  = 0x401e;
  uint32 ple_gap                 = 0x4020;
  uint32 ple_window              = 0x4022;

  # 32 bit read only data fields 
  uint32 instr_error             = 0x4400;
  uint32 exit_reason             = 0x4402;
  uint32 int_info                = 0x4404;
  uint32 int_ec                  = 0x4406;
  uint32 idt_vec_info_field      = 0x4408;
  uint32 idt_vec_ec              = 0x440a;
  uint32 exit_instr_len          = 0x440c;
  uint32 exit_instr_info         = 0x440e;


  uint32 guest_es_limit          = 0x4800;
  uint32 guest_cs_limit          = 0x4802;
  uint32 guest_ss_limit          = 0x4804;
  uint32 guest_ds_limit          = 0x4806;
  uint32 guest_fs_limit          = 0x4808;
  uint32 guest_gs_limit          = 0x480a;
  uint32 guest_ldtr_limit        = 0x480c;
  uint32 guest_tr_limit          = 0x480e;
  uint32 guest_gdtr_limit        = 0x4810;
  uint32 guest_idtr_limit        = 0x4812;
  uint32 guest_es_attr           = 0x4814;
  uint32 guest_cs_attr           = 0x4816;
  uint32 guest_ss_attr           = 0x4818;
  uint32 guest_ds_attr           = 0x481a;
  uint32 guest_fs_attr           = 0x481c;
  uint32 guest_gs_attr           = 0x481e;
  uint32 guest_ldtr_attr         = 0x4820;
  uint32 guest_tr_attr           = 0x4822;
  uint32 guest_interruptibility_info = 0x4824;
  uint32 guest_activity_state    = 0x4826;
  uint32 guest_smbase            = 0x4828;
  uint32 guest_ia32_sysenter_cs  = 0x482a;
  uint32 preemption_timer_value  = 0x482e;

  # 32 bit host-state fields
  uint32 host_ia32_sysenter_cs  = 0x4c00;

  # natural-width control fields
  uint32 cr0_mask                = 0x6000;
  uint32 cr4_mask                = 0x6002;
  uint32 cr0_read_shadow         = 0x6004;
  uint32 cr4_read_shadow         = 0x6006;
  uint32 cr3_target_0            = 0x6008;
  uint32 cr3_target_1            = 0x600a;
  uint32 cr3_target_2            = 0x600c;
  uint32 cr3_target_3            = 0x600e;

  # natural-width read only fields 
  uint32 exit_qualification      = 0x6400;
  uint32 io_rcx                  = 0x6402;
  uint32 io_rsi                  = 0x6404;
  uint32 io_rdi                  = 0x6406;
  uint32 io_rip                  = 0x6408;
  uint32 guest_linear_addr       = 0x640a;

  # nature-width guest-state fields
  uint32 guest_cr0              = 0x6800;
  uint32 guest_cr3              = 0x6802;
  uint32 guest_cr4              = 0x6804;
  uint32 guest_es_base          = 0x6806;
  uint32 guest_cs_base          = 0x6808;
  uint32 guest_ss_base          = 0x680a;
  uint32 guest_ds_base          = 0x680c;
  uint32 guest_fs_base          = 0x680e;
  uint32 guest_gs_base          = 0x6810;
  uint32 guest_ldtr_base        = 0x6812;
  uint32 guest_tr_base          = 0x6814;
  uint32 guest_gdtr_base        = 0x6816;
  uint32 guest_idtr_base        = 0x6818;
  uint32 guest_dr7              = 0x681a;
  uint32 guest_rsp              = 0x681c;
  uint32 guest_rip              = 0x681e;
  uint32 guest_rflags           = 0x6820;
  uint32 guest_pending_debug_except = 0x6822;
  uint32 guest_ia32_sysenter_esp    = 0x6824;
  uint32 guest_ia32_sysenter_eip    = 0x6826;

  # nature-width host-state fields
  uint64 host_cr0               = 0x6c00;
  uint64 host_cr3               = 0x6c02;
  uint64 host_cr4               = 0x6c04;
  uint64 host_fs_base           = 0x6c06;
  uint64 host_gs_base           = 0x6c08;
  uint64 host_tr_base           = 0x6c0a;
  uint64 host_gdtr_base         = 0x6c0c;
  uint64 host_idtr_base         = 0x6c0e;
  uint64 host_ia32_sysenter_esp = 0x6c10;
  uint64 host_ia32_sysenter_eip = 0x6c12;
  uint64 host_rsp               = 0x6c14;
  uint64 host_rip               = 0x6c16; 

}

END;

